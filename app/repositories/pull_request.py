from datetime import datetime

from sqlalchemy import and_, func, or_, select, text
from sqlalchemy.orm import Session, aliased, contains_eager, joinedload, subqueryload

from app.models.ai_analysis import AiAnalysis, ConflictCheck
from app.models.audit_log import AuditLog
from app.models.merge import Merge
from app.models.pull_request import PullRequest, RejectReason, ViewLog
from app.models.repository import Repository
from app.models.user import User
from app.models.enums import PullRequestStatus, Visibility


def get_repository_by_id(db: Session, repo_id: int) -> Repository | None:
    return db.get(Repository, repo_id)


def get_pr_by_id(db: Session, pr_id: int) -> PullRequest | None:
    return db.get(PullRequest, pr_id)


def get_pr_with_repository(db: Session, pr_id: int) -> PullRequest | None:
    stmt = (
        select(PullRequest)
        .options(joinedload(PullRequest.repository))
        .where(PullRequest.id == pr_id)
    )
    return db.scalar(stmt)


def get_draft_by_user_and_repo(db: Session, user_id: int, repo_id: int) -> PullRequest | None:
    stmt = select(PullRequest).where(
        PullRequest.author_id == user_id,
        PullRequest.repository_id == repo_id,
        PullRequest.status == PullRequestStatus.DRAFT,
    )
    return db.scalar(stmt)


def create_pr(db: Session, *, repository_id: int, author_id: int, now: datetime) -> PullRequest:
    pr = PullRequest(
        repository_id=repository_id,
        author_id=author_id,
        status=PullRequestStatus.DRAFT,
        first_drafted_at=now,
        last_saved_at=now,
        save_count=0,
    )
    db.add(pr)
    db.flush()
    db.refresh(pr)
    return pr


def get_latest_ai_analysis(db: Session, pr_id: int) -> AiAnalysis | None:
    stmt = (
        select(AiAnalysis)
        .where(AiAnalysis.pull_request_id == pr_id)
        .order_by(AiAnalysis.run_seq.desc())
        .limit(1)
    )
    return db.scalar(stmt)


def get_ai_analysis_by_run_seq(db: Session, pr_id: int, run_seq: int) -> AiAnalysis | None:
    stmt = select(AiAnalysis).where(
        AiAnalysis.pull_request_id == pr_id,
        AiAnalysis.run_seq == run_seq,
    )
    return db.scalar(stmt)


def get_next_run_seq(db: Session, pr_id: int) -> int:
    stmt = select(func.max(AiAnalysis.run_seq)).where(AiAnalysis.pull_request_id == pr_id)
    current_max = db.scalar(stmt)
    return (current_max or 0) + 1


def get_pr_for_detail(db: Session, pr_id: int) -> PullRequest | None:
    stmt = (
        select(PullRequest)
        .options(
            joinedload(PullRequest.repository).joinedload(Repository.author),
            joinedload(PullRequest.author),
            joinedload(PullRequest.merge),
            subqueryload(PullRequest.view_logs),
            subqueryload(PullRequest.analyses),
            subqueryload(PullRequest.reject_reasons),
        )
        .where(PullRequest.id == pr_id)
    )
    return db.scalar(stmt)


def get_active_reject_reason(pr: PullRequest) -> RejectReason | None:
    for rr in pr.reject_reasons:
        if rr.superseded_at is None:
            return rr
    return None


def create_view_log(
    db: Session,
    *,
    pr_id: int,
    viewer_id: int,
    ip_hash: str,
    day_bucket_hash: str,
    now: datetime,
) -> ViewLog:
    vl = ViewLog(
        pull_request_id=pr_id,
        viewer_id=viewer_id,
        ip_hash=ip_hash,
        day_bucket_hash=day_bucket_hash,
        viewed_at=now,
    )
    db.add(vl)
    db.flush()
    return vl


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
) -> tuple[list[tuple[PullRequest, AiAnalysis | None]], int]:
    latest_seq_sq = (
        select(func.max(AiAnalysis.run_seq))
        .where(AiAnalysis.pull_request_id == PullRequest.id)
        .correlate(PullRequest)
        .scalar_subquery()
    )
    LatestAnalysis = aliased(AiAnalysis)

    base = (
        select(PullRequest, LatestAnalysis)
        .outerjoin(
            LatestAnalysis,
            and_(
                LatestAnalysis.pull_request_id == PullRequest.id,
                LatestAnalysis.run_seq == latest_seq_sq,
            ),
        )
        .options(
            joinedload(PullRequest.repository),
            joinedload(PullRequest.author),
        )
    )

    # 접근 제어: PUBLIC 또는 본인 PRIVATE
    if current_user_id is not None:
        base = base.where(
            or_(
                PullRequest.visibility == Visibility.PUBLIC,
                and_(
                    PullRequest.visibility == Visibility.PRIVATE,
                    PullRequest.author_id == current_user_id,
                ),
            )
        )
    else:
        base = base.where(PullRequest.visibility == Visibility.PUBLIC)

    # DRAFT 제외 (목록은 제출 이후만)
    base = base.where(PullRequest.status != PullRequestStatus.DRAFT)

    if repo_id is not None:
        base = base.where(PullRequest.repository_id == repo_id)

    if author_username:
        AuthorUser = aliased(User)
        base = base.join(AuthorUser, PullRequest.author_id == AuthorUser.id).where(
            AuthorUser.username == author_username
        )

    if statuses:
        base = base.where(PullRequest.status.in_(statuses))

    if contribution_type:
        base = base.where(
            text("JSON_CONTAINS(pull_requests.contribution_types, :val)").bindparams(
                val=f'"{contribution_type}"'
            )
        )

    if grade:
        base = base.where(LatestAnalysis.ai_grade == grade)

    count_stmt = select(func.count()).select_from(base.subquery())
    total = db.scalar(count_stmt) or 0

    rows_stmt = (
        base
        .order_by(PullRequest.submitted_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    rows = db.execute(rows_stmt).all()
    return [(row[0], row[1]) for row in rows], total


def create_reject_reason(
    db: Session,
    *,
    pr_id: int,
    category: str,
    detail: str,
    created_by: int,
    now: datetime,
) -> RejectReason:
    rr = RejectReason(
        pull_request_id=pr_id,
        category=category,
        detail=detail,
        created_by=created_by,
        created_at=now,
    )
    db.add(rr)
    db.flush()
    return rr


def get_active_reject_reason_by_pr_id(db: Session, pr_id: int) -> RejectReason | None:
    stmt = (
        select(RejectReason)
        .where(RejectReason.pull_request_id == pr_id, RejectReason.superseded_at == None)
        .limit(1)
    )
    return db.scalar(stmt)


def supersede_reject_reason(db: Session, rr: RejectReason, new_id: int, now: datetime) -> None:
    rr.superseded_by_id = new_id
    rr.superseded_at = now


def create_merge(
    db: Session,
    *,
    pr_id: int,
    repo_id: int,
    contributor_id: int,
    author_id: int,
    final_grade: str,
    credit_text: str,
    readme_apply_note: str | None,
    comment: str | None,
    merged_at: datetime,
) -> Merge:
    m = Merge(
        pull_request_id=pr_id,
        repository_id=repo_id,
        contributor_id=contributor_id,
        author_id=author_id,
        final_grade=final_grade,
        credit_text=credit_text,
        readme_apply_note=readme_apply_note,
        author_comment=comment,
        citation_url="",
        merged_at=merged_at,
    )
    db.add(m)
    db.flush()
    return m


def create_ai_analysis(
    db: Session,
    *,
    pull_request_id: int,
    run_seq: int,
    generated_title: str,
    summary: str,
    structured_content: dict,
    contribution_types: list[str],
    score_scope: int,
    score_permanence: int,
    score_cascade: int,
    score_alignment: int,
    score_specificity: int,
    score_total: int,
    ai_grade: str,
    rationale: str,
    missing_info: list[str],
    conflict_checks_data: list[dict],
    model_name: str,
    now: datetime,
) -> AiAnalysis:
    analysis = AiAnalysis(
        pull_request_id=pull_request_id,
        run_seq=run_seq,
        generated_title=generated_title,
        summary=summary,
        structured_content=structured_content,
        contribution_types=contribution_types,
        score_scope=score_scope,
        score_permanence=score_permanence,
        score_cascade=score_cascade,
        score_alignment=score_alignment,
        score_specificity=score_specificity,
        score_total=score_total,
        ai_grade=ai_grade,
        rationale=rationale,
        missing_info=missing_info,
        model_name=model_name,
        created_at=now,
    )
    db.add(analysis)
    db.flush()

    for cc in conflict_checks_data:
        db.add(ConflictCheck(
            ai_analysis_id=analysis.id,
            risk_level=cc["risk_level"],
            check_target=cc["check_target"],
            passed=cc["passed"],
            detail=cc.get("detail", ""),
            created_at=now,
        ))

    db.flush()
    db.refresh(analysis)
    return analysis
