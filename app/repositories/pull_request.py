from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.ai_analysis import AiAnalysis, ConflictCheck
from app.models.pull_request import PullRequest
from app.models.repository import Repository
from app.models.enums import PullRequestStatus


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
