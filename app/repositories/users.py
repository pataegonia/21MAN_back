from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.ai_analysis import AiAnalysis
from app.models.enums import PullRequestStatus
from app.models.merge import Merge
from app.models.pull_request import PullRequest
from app.models.repository import Repository, RepositoryTag, Tag
from app.models.user import User


def get_user_by_username(db: Session, username: str) -> User | None:
    statement = select(User).where(func.lower(User.username) == username.lower())
    return db.scalar(statement)


def count_user_repositories(db: Session, user_id: int) -> int:
    statement = select(func.count(Repository.id)).where(Repository.author_id == user_id)
    return db.scalar(statement) or 0


def count_user_submitted_prs(db: Session, user_id: int) -> int:
    statement = select(func.count(PullRequest.id)).where(
        PullRequest.author_id == user_id,
        PullRequest.status != PullRequestStatus.DRAFT,
    )
    return db.scalar(statement) or 0


def count_user_merged_contributions(db: Session, user_id: int) -> int:
    statement = select(func.count(Merge.id)).where(Merge.contributor_id == user_id)
    return db.scalar(statement) or 0


def count_statement(db: Session, statement: Select) -> int:
    return db.scalar(select(func.count()).select_from(statement.subquery())) or 0


def get_repository_tags(db: Session, repository_ids: list[int]) -> dict[int, list[str]]:
    if not repository_ids:
        return {}
    statement = (
        select(RepositoryTag.repository_id, Tag.name)
        .join(Tag, Tag.id == RepositoryTag.tag_id)
        .where(RepositoryTag.repository_id.in_(repository_ids))
        .order_by(Tag.name)
    )
    tags: dict[int, list[str]] = {repo_id: [] for repo_id in repository_ids}
    for repo_id, tag_name in db.execute(statement):
        tags.setdefault(repo_id, []).append(tag_name)
    return tags


def get_latest_ai_grades(db: Session, pull_request_ids: list[int]) -> dict[int, str]:
    if not pull_request_ids:
        return {}

    latest_runs = (
        select(
            AiAnalysis.pull_request_id.label("pull_request_id"),
            func.max(AiAnalysis.run_seq).label("run_seq"),
        )
        .where(AiAnalysis.pull_request_id.in_(pull_request_ids))
        .group_by(AiAnalysis.pull_request_id)
        .subquery()
    )
    statement = (
        select(AiAnalysis.pull_request_id, AiAnalysis.ai_grade)
        .join(
            latest_runs,
            (AiAnalysis.pull_request_id == latest_runs.c.pull_request_id)
            & (AiAnalysis.run_seq == latest_runs.c.run_seq),
        )
    )
    return {pr_id: ai_grade for pr_id, ai_grade in db.execute(statement)}
