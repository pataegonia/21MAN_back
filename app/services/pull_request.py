import json
from datetime import UTC, date, datetime
from hashlib import sha256

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AppError
from app.models.ai_analysis import AiAnalysis
from app.models.audit_log import AuditLog
from app.models.enums import ContributionGrade, PullRequestStatus, Visibility
from app.models.merge import Merge
from app.models.notification import Notification
from app.models.pull_request import PullRequest, RejectReason
from app.repositories import pull_request as pr_repo


def _now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def _add_pr_notification(
    db: Session,
    *,
    recipient_id: int,
    notification_type: str,
    pr: PullRequest,
    actor_id: int,
    now: datetime,
    extra_payload: dict | None = None,
) -> None:
    payload = {
        "pr_id": pr.id,
        "pr_title": pr.title,
        "repo_id": pr.repository_id,
        "repo_title": pr.repository.title if pr.repository else None,
        "actor_id": actor_id,
    }
    if extra_payload:
        payload.update(extra_payload)
    db.add(Notification(
        recipient_id=recipient_id,
        type=notification_type,
        payload=payload,
        created_at=now,
    ))


# ---------------------------------------------------------------------------
# Draft CRUD
# ---------------------------------------------------------------------------

def create_or_get_draft(db: Session, *, repo_id: int, user_id: int) -> tuple[PullRequest, bool]:
    repo = pr_repo.get_repository_by_id(db, repo_id)
    if repo is None:
        raise AppError("REPOSITORY_NOT_FOUND", "존재하지 않는 Repository입니다.", status_code=404)

    existing = pr_repo.get_draft_by_user_and_repo(db, user_id=user_id, repo_id=repo_id)
    if existing is not None:
        return existing, False

    now = _now()
    pr = pr_repo.create_pr(db, repository_id=repo_id, author_id=user_id, now=now)
    db.commit()
    db.refresh(pr)
    return pr, True


def get_draft(db: Session, *, pr_id: int, user_id: int) -> PullRequest:
    pr = pr_repo.get_pr_with_repository(db, pr_id)
    if pr is None:
        raise AppError("PR_NOT_FOUND", "존재하지 않는 PR입니다.", status_code=404)
    if pr.author_id != user_id:
        raise AppError("FORBIDDEN", "본인의 Draft만 조회할 수 있습니다.", status_code=403)
    return pr


def save_draft(db: Session, *, pr_id: int, user_id: int, raw_content: str) -> PullRequest:
    pr = pr_repo.get_pr_by_id(db, pr_id)
    if pr is None:
        raise AppError("PR_NOT_FOUND", "존재하지 않는 PR입니다.", status_code=404)
    if pr.author_id != user_id:
        raise AppError("FORBIDDEN", "본인의 Draft만 수정할 수 있습니다.", status_code=403)
    if pr.status != PullRequestStatus.DRAFT:
        raise AppError("PR_NOT_DRAFT", "DRAFT 상태의 PR만 저장할 수 있습니다.", status_code=400)

    pr.raw_content = raw_content
    pr.last_saved_at = _now()
    pr.save_count += 1
    db.commit()
    db.refresh(pr)
    return pr


# ---------------------------------------------------------------------------
# AI Analysis
# ---------------------------------------------------------------------------

_AI_MODEL = "gpt-4o-2024-08-06"

_SYSTEM_PROMPT = """당신은 세계관 창작 프로젝트의 기여 제안(PR)을 분석하는 전문 AI입니다.
주어진 PR 내용을 분석하여 다음 JSON 형식으로만 응답하세요. 다른 텍스트는 포함하지 마세요.

{
  "generated_title": "PR을 대표하는 간결한 제목 (최대 50자)",
  "summary": "PR 내용 요약 (1-3문장)",
  "structured_content": { "핵심 내용을 구조화한 객체" },
  "contribution_types": ["character_add|character_modify|worldbuilding|lore|event|location|rule|other 중 해당하는 것들"],
  "score_scope": 0~10,
  "score_permanence": 0~10,
  "score_cascade": 0~10,
  "score_alignment": 0~10,
  "score_specificity": 0~10,
  "rationale": "점수 산정 근거 설명",
  "missing_info": ["누락된 정보 목록"],
  "conflict_checks": [
    {
      "risk_level": "LOW|MEDIUM|HIGH",
      "check_target": "readme|forbidden_settings|contribution_guideline|other",
      "passed": true/false,
      "detail": "검사 결과 설명"
    }
  ]
}

점수 기준:
- score_scope: PR이 영향을 미치는 세계관의 범위 (0=없음, 10=전체)
- score_permanence: 설정의 영속성/중요도 (0=임시, 10=핵심 설정)
- score_cascade: 다른 설정에 미치는 파급 효과 (0=없음, 10=전면적)
- score_alignment: 기존 세계관과의 정합성 (0=충돌, 10=완벽 조화)
- score_specificity: 내용의 구체성/완성도 (0=모호, 10=매우 구체적)"""


def _build_user_prompt(pr: PullRequest) -> str:
    repo = pr.repository
    parts = [f"## PR 내용\n{pr.raw_content}"]

    if repo.readme_overview:
        parts.append(f"## 세계관 README\n{repo.readme_overview}")
    if repo.contribution_guideline:
        parts.append(f"## 기여 가이드라인\n{repo.contribution_guideline}")
    if repo.forbidden_items:
        forbidden_names = [item.content for item in repo.forbidden_items]
        parts.append(f"## 금지 항목\n" + "\n".join(f"- {n}" for n in forbidden_names))

    return "\n\n".join(parts)


def _grade_from_score(score_total: int) -> str:
    if score_total >= 35:
        return ContributionGrade.MAJOR
    if score_total >= 20:
        return ContributionGrade.NORMAL
    return ContributionGrade.MINOR


def _call_openai(pr: PullRequest) -> dict:
    from openai import OpenAI

    if not settings.openai_api_key:
        raise AppError("AI_SERVICE_ERROR", "AI 분석에 실패했습니다. 잠시 후 다시 시도해주세요.", status_code=502)

    client = OpenAI(api_key=settings.openai_api_key)
    try:
        response = client.chat.completions.create(
            model=_AI_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_prompt(pr)},
            ],
            temperature=0.3,
        )
        return json.loads(response.choices[0].message.content)
    except Exception as exc:
        raise AppError("AI_SERVICE_ERROR", "AI 분석에 실패했습니다. 잠시 후 다시 시도해주세요.", status_code=502) from exc


def analyze_pr(db: Session, *, pr_id: int, user_id: int) -> AiAnalysis:
    pr = pr_repo.get_pr_with_repository(db, pr_id)
    if pr is None:
        raise AppError("PR_NOT_FOUND", "존재하지 않는 PR입니다.", status_code=404)
    if pr.author_id != user_id:
        raise AppError("FORBIDDEN", "본인의 PR만 분석 요청할 수 있습니다.", status_code=403)
    if not pr.raw_content or not pr.raw_content.strip():
        raise AppError("CONTENT_REQUIRED", "분석할 내용이 없습니다. 먼저 내용을 작성해주세요.", status_code=400)

    result = _call_openai(pr)

    score_total = (
        result.get("score_scope", 0)
        + result.get("score_permanence", 0)
        + result.get("score_cascade", 0)
        + result.get("score_alignment", 0)
        + result.get("score_specificity", 0)
    )
    ai_grade = _grade_from_score(score_total)
    run_seq = pr_repo.get_next_run_seq(db, pr_id)
    now = _now()

    analysis = pr_repo.create_ai_analysis(
        db,
        pull_request_id=pr_id,
        run_seq=run_seq,
        generated_title=result.get("generated_title", ""),
        summary=result.get("summary", ""),
        structured_content=result.get("structured_content", {}),
        contribution_types=result.get("contribution_types", []),
        score_scope=result.get("score_scope", 0),
        score_permanence=result.get("score_permanence", 0),
        score_cascade=result.get("score_cascade", 0),
        score_alignment=result.get("score_alignment", 0),
        score_specificity=result.get("score_specificity", 0),
        score_total=score_total,
        ai_grade=ai_grade,
        rationale=result.get("rationale", ""),
        missing_info=result.get("missing_info", []),
        conflict_checks_data=result.get("conflict_checks", []),
        model_name=_AI_MODEL,
        now=now,
    )
    db.commit()
    db.refresh(analysis)

    # conflict_checks eager load
    _ = analysis.conflict_checks
    return analysis


def get_ai_analysis(db: Session, *, pr_id: int, user_id: int, run_seq: int | None = None) -> AiAnalysis:
    pr = pr_repo.get_pr_with_repository(db, pr_id)
    if pr is None:
        raise AppError("PR_NOT_FOUND", "존재하지 않는 PR입니다.", status_code=404)

    repo = pr.repository
    if pr.author_id != user_id and repo.author_id != user_id:
        raise AppError("FORBIDDEN", "PR 작성자 또는 원작자만 AI 분석 결과를 조회할 수 있습니다.", status_code=403)

    if run_seq is not None:
        analysis = pr_repo.get_ai_analysis_by_run_seq(db, pr_id, run_seq)
    else:
        analysis = pr_repo.get_latest_ai_analysis(db, pr_id)

    if analysis is None:
        raise AppError("ANALYSIS_NOT_FOUND", "AI 분석 결과가 없습니다.", status_code=404)

    _ = analysis.conflict_checks
    return analysis


# ---------------------------------------------------------------------------
# Submit & Contributor Comment
# ---------------------------------------------------------------------------

def submit_pr(db: Session, *, pr_id: int, user_id: int, visibility: str) -> PullRequest:
    pr = pr_repo.get_pr_with_repository(db, pr_id)
    if pr is None:
        raise AppError("PR_NOT_FOUND", "존재하지 않는 PR입니다.", status_code=404)
    if pr.author_id != user_id:
        raise AppError("FORBIDDEN", "본인의 PR만 제출할 수 있습니다.", status_code=403)
    if pr.status not in (PullRequestStatus.DRAFT, PullRequestStatus.CHANGES_REQUESTED):
        raise AppError("INVALID_STATUS_TRANSITION", "DRAFT 또는 CHANGES_REQUESTED 상태의 PR만 제출할 수 있습니다.", status_code=400)

    now = _now()
    previous_status = pr.status
    pr.status = PullRequestStatus.SUBMITTED
    pr.submitted_at = now
    pr.visibility = Visibility(visibility)

    repo = pr.repository
    _add_pr_notification(
        db,
        recipient_id=repo.author_id,
        notification_type="PR_RESUBMITTED" if previous_status == PullRequestStatus.CHANGES_REQUESTED else "PR_SUBMITTED",
        pr=pr,
        actor_id=user_id,
        now=now,
    )
    db.add(AuditLog(
        actor_id=user_id,
        action_type="PR_SUBMIT",
        target_type="pull_request",
        target_id=pr_id,
        payload={"visibility": visibility},
        created_at=now,
    ))

    db.commit()
    db.refresh(pr)
    return pr


def save_contributor_comment(db: Session, *, pr_id: int, user_id: int, comment: str) -> PullRequest:
    pr = pr_repo.get_pr_with_repository(db, pr_id)
    if pr is None:
        raise AppError("PR_NOT_FOUND", "존재하지 않는 PR입니다.", status_code=404)
    if pr.author_id != user_id:
        raise AppError("FORBIDDEN", "본인의 PR에만 의견을 작성할 수 있습니다.", status_code=403)

    now = _now()
    pr.contributor_comment = comment
    _add_pr_notification(
        db,
        recipient_id=pr.repository.author_id,
        notification_type="PR_COMMENT_ADDED",
        pr=pr,
        actor_id=user_id,
        now=now,
    )
    db.commit()
    db.refresh(pr)
    return pr


# ---------------------------------------------------------------------------
# PR 조회 (05-pull-requests-query)
# ---------------------------------------------------------------------------

def get_pr_detail(
    db: Session,
    *,
    pr_id: int,
    current_user_id: int | None,
    ip_hash: str,
) -> tuple[PullRequest, bool]:
    pr = pr_repo.get_pr_for_detail(db, pr_id)
    if pr is None:
        raise AppError("PR_NOT_FOUND", "존재하지 않는 PR입니다.", status_code=404)

    if pr.visibility == Visibility.PRIVATE:
        if not current_user_id:
            raise AppError("FORBIDDEN", "열람 권한이 없습니다.", status_code=403)
        if current_user_id != pr.author_id and current_user_id != pr.repository.author_id:
            raise AppError("FORBIDDEN", "열람 권한이 없습니다.", status_code=403)

    if (
        current_user_id
        and current_user_id == pr.repository.author_id
        and current_user_id != pr.author_id
    ):
        now = _now()
        day_bucket_hash = sha256(f"{ip_hash}:{date.today()}".encode()).hexdigest()
        pr_repo.create_view_log(
            db,
            pr_id=pr_id,
            viewer_id=current_user_id,
            ip_hash=ip_hash,
            day_bucket_hash=day_bucket_hash,
            now=now,
        )
        db.add(AuditLog(
            actor_id=current_user_id,
            action_type="PR_VIEW",
            target_type="pull_request",
            target_id=pr_id,
            payload={},
            created_at=now,
        ))
        db.commit()
        db.refresh(pr)

    is_owner = current_user_id == pr.author_id
    return pr, is_owner


def list_prs(
    db: Session,
    *,
    repo_id: int | None,
    author_username: str | None,
    statuses: list[str],
    contribution_type: str | None,
    grade: str | None,
    current_user_id: int | None,
    page: int,
    size: int,
) -> tuple[list, int]:
    size = min(size, 100)
    return pr_repo.list_prs(
        db,
        repo_id=repo_id,
        author_username=author_username,
        statuses=statuses,
        contribution_type=contribution_type,
        grade=grade,
        current_user_id=current_user_id,
        page=page,
        size=size,
    )


# ---------------------------------------------------------------------------
# PR 원작자 액션 (06-pull-requests-actions)
# ---------------------------------------------------------------------------

def _assert_repo_author(pr: PullRequest, user_id: int, action_msg: str) -> None:
    if pr.repository.author_id != user_id:
        raise AppError("FORBIDDEN", action_msg, status_code=403)


def accept_pr(db: Session, *, pr_id: int, user_id: int, comment: str | None) -> PullRequest:
    pr = pr_repo.get_pr_with_repository(db, pr_id)
    if pr is None:
        raise AppError("PR_NOT_FOUND", "존재하지 않는 PR입니다.", status_code=404)
    _assert_repo_author(pr, user_id, "원작자만 PR을 수락할 수 있습니다.")
    if pr.status != PullRequestStatus.SUBMITTED:
        raise AppError("INVALID_STATUS_TRANSITION", "SUBMITTED 상태의 PR만 수락할 수 있습니다.", status_code=400)

    now = _now()
    pr.status = PullRequestStatus.ACCEPTED
    pr.reviewed_at = now
    pr.author_review_comment = comment
    _add_pr_notification(
        db,
        recipient_id=pr.author_id,
        notification_type="PR_ACCEPTED",
        pr=pr,
        actor_id=user_id,
        now=now,
        extra_payload={"comment": comment} if comment else None,
    )
    db.add(AuditLog(
        actor_id=user_id,
        action_type="PR_ACCEPT",
        target_type="pull_request",
        target_id=pr_id,
        payload={},
        created_at=now,
    ))
    db.commit()
    db.refresh(pr)
    return pr


def request_changes(
    db: Session, *, pr_id: int, user_id: int, reason: str, comment: str | None
) -> PullRequest:
    pr = pr_repo.get_pr_with_repository(db, pr_id)
    if pr is None:
        raise AppError("PR_NOT_FOUND", "존재하지 않는 PR입니다.", status_code=404)
    _assert_repo_author(pr, user_id, "원작자만 수정을 요청할 수 있습니다.")
    if pr.status != PullRequestStatus.SUBMITTED:
        raise AppError("INVALID_STATUS_TRANSITION", "SUBMITTED 상태의 PR에만 수정을 요청할 수 있습니다.", status_code=400)

    now = _now()
    pr.status = PullRequestStatus.CHANGES_REQUESTED
    pr.reviewed_at = now
    pr.changes_requested_reason = reason
    pr.author_review_comment = comment
    extra_payload = {"reason": reason}
    if comment:
        extra_payload["comment"] = comment
    _add_pr_notification(
        db,
        recipient_id=pr.author_id,
        notification_type="PR_CHANGES_REQUESTED",
        pr=pr,
        actor_id=user_id,
        now=now,
        extra_payload=extra_payload,
    )
    db.add(AuditLog(
        actor_id=user_id,
        action_type="PR_REQUEST_CHANGES",
        target_type="pull_request",
        target_id=pr_id,
        payload={},
        created_at=now,
    ))
    db.commit()
    db.refresh(pr)
    return pr


def reject_pr(
    db: Session, *, pr_id: int, user_id: int, category: str, detail: str
) -> tuple[PullRequest, "RejectReason"]:
    pr = pr_repo.get_pr_with_repository(db, pr_id)
    if pr is None:
        raise AppError("PR_NOT_FOUND", "존재하지 않는 PR입니다.", status_code=404)
    _assert_repo_author(pr, user_id, "원작자만 PR을 거절할 수 있습니다.")
    if pr.status != PullRequestStatus.SUBMITTED:
        raise AppError("INVALID_STATUS_TRANSITION", "SUBMITTED 상태의 PR만 거절할 수 있습니다.", status_code=400)

    now = _now()
    pr.status = PullRequestStatus.REJECTED
    pr.reviewed_at = now
    rr = pr_repo.create_reject_reason(db, pr_id=pr_id, category=category, detail=detail, created_by=user_id, now=now)
    _add_pr_notification(
        db,
        recipient_id=pr.author_id,
        notification_type="PR_REJECTED",
        pr=pr,
        actor_id=user_id,
        now=now,
        extra_payload={"reject_category": category, "reject_detail": detail},
    )
    db.add(AuditLog(
        actor_id=user_id,
        action_type="PR_REJECT",
        target_type="pull_request",
        target_id=pr_id,
        payload={"category": category},
        created_at=now,
    ))
    db.commit()
    db.refresh(pr)
    db.refresh(rr)
    return pr, rr


def merge_pr(
    db: Session,
    *,
    pr_id: int,
    user_id: int,
    credit_text: str,
    readme_apply_note: str | None,
    comment: str | None,
    final_grade: str | None,
) -> Merge:
    pr = pr_repo.get_pr_with_repository(db, pr_id)
    if pr is None:
        raise AppError("PR_NOT_FOUND", "존재하지 않는 PR입니다.", status_code=404)
    _assert_repo_author(pr, user_id, "원작자만 PR을 병합할 수 있습니다.")
    if pr.status not in (PullRequestStatus.ACCEPTED, PullRequestStatus.SUBMITTED):
        raise AppError(
            "INVALID_STATUS_TRANSITION",
            f"{pr.status} 상태의 PR은 병합할 수 없습니다.",
            status_code=400,
        )

    if not final_grade:
        if pr.author_grade_override:
            final_grade = pr.author_grade_override
        else:
            latest = pr_repo.get_latest_ai_analysis(db, pr_id)
            final_grade = latest.ai_grade if latest else ContributionGrade.NORMAL

    now = _now()
    pr.status = PullRequestStatus.MERGED
    pr.merged_at = now

    m = pr_repo.create_merge(
        db,
        pr_id=pr_id,
        repo_id=pr.repository_id,
        contributor_id=pr.author_id,
        author_id=user_id,
        final_grade=final_grade,
        credit_text=credit_text,
        readme_apply_note=readme_apply_note,
        comment=comment,
        merged_at=now,
    )
    m.citation_url = f"{settings.site_url}/m/{m.id}"

    _add_pr_notification(
        db,
        recipient_id=pr.author_id,
        notification_type="PR_MERGED",
        pr=pr,
        actor_id=user_id,
        now=now,
        extra_payload={
            "final_grade": final_grade.value if isinstance(final_grade, ContributionGrade) else final_grade,
            "merge_id": m.id,
            "citation_url": m.citation_url,
        },
    )
    db.add(AuditLog(
        actor_id=user_id,
        action_type="PR_MERGE",
        target_type="pull_request",
        target_id=pr_id,
        payload={"final_grade": final_grade},
        created_at=now,
    ))
    db.commit()
    db.refresh(m)
    return m


def grade_override(
    db: Session, *, pr_id: int, user_id: int, grade: str, reason: str | None
) -> PullRequest:
    pr = pr_repo.get_pr_with_repository(db, pr_id)
    if pr is None:
        raise AppError("PR_NOT_FOUND", "존재하지 않는 PR입니다.", status_code=404)
    _assert_repo_author(pr, user_id, "원작자만 등급을 조정할 수 있습니다.")

    latest = pr_repo.get_latest_ai_analysis(db, pr_id)
    if latest and latest.ai_grade != grade and not reason:
        raise AppError("VALIDATION_ERROR", "AI 등급과 다른 경우 조정 사유를 입력해야 합니다.", status_code=422)

    now = _now()
    pr.author_grade_override = grade
    pr.author_grade_override_reason = reason
    extra_payload = {
        "ai_grade": latest.ai_grade if latest else None,
        "override_grade": grade,
    }
    if reason:
        extra_payload["override_reason"] = reason
    _add_pr_notification(
        db,
        recipient_id=pr.author_id,
        notification_type="GRADE_ADJUSTED",
        pr=pr,
        actor_id=user_id,
        now=now,
        extra_payload=extra_payload,
    )
    db.add(AuditLog(
        actor_id=user_id,
        action_type="PR_GRADE_OVERRIDE",
        target_type="pull_request",
        target_id=pr_id,
        payload={"grade": grade},
        created_at=now,
    ))
    db.commit()
    db.refresh(pr)
    return pr


def update_reject_reason(
    db: Session, *, pr_id: int, user_id: int, category: str, detail: str
) -> "RejectReason":
    pr = pr_repo.get_pr_with_repository(db, pr_id)
    if pr is None:
        raise AppError("PR_NOT_FOUND", "존재하지 않는 PR입니다.", status_code=404)
    _assert_repo_author(pr, user_id, "원작자만 거절 사유를 수정할 수 있습니다.")
    if pr.status != PullRequestStatus.REJECTED:
        raise AppError("PR_NOT_REJECTED", "REJECTED 상태의 PR에만 거절 사유를 수정할 수 있습니다.", status_code=400)

    now = _now()
    old_rr = pr_repo.get_active_reject_reason_by_pr_id(db, pr_id)
    new_rr = pr_repo.create_reject_reason(db, pr_id=pr_id, category=category, detail=detail, created_by=user_id, now=now)
    if old_rr:
        pr_repo.supersede_reject_reason(db, old_rr, new_rr.id, now)
    db.add(AuditLog(
        actor_id=user_id,
        action_type="PR_UPDATE_REJECT_REASON",
        target_type="pull_request",
        target_id=pr_id,
        payload={"category": category},
        created_at=now,
    ))
    db.commit()
    db.refresh(new_rr)
    return new_rr
