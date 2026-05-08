from datetime import datetime

from sqlalchemy import case, desc, func, select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.audit_log import AuditLog
from app.models.enums import ContributionGrade, PullRequestStatus, Visibility
from app.models.merge import Merge
from app.models.pull_request import PullRequest
from app.models.repository import Repository
from app.models.user import User
from app.repositories import users as user_repo
from app.schemas.users import (
    AuthorStatsResponse,
    BadgesResponse,
    ContributionSummary,
    ContributorStatsResponse,
    PageResponse,
    PublicUserProfile,
    PullRequestNestedSummary,
    PullRequestSummary,
    RepositoryNestedSummary,
    RepositorySummary,
    UserProfileUpdateRequest,
)

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
REVIEWED_STATUSES = {
    PullRequestStatus.ACCEPTED,
    PullRequestStatus.CHANGES_REQUESTED,
    PullRequestStatus.REJECTED,
    PullRequestStatus.MERGED,
}
AUTHOR_REVIEW_ACTIONS = (
    "PR_ACCEPT",
    "PR_REQUEST_CHANGES",
    "PR_REJECT",
    "PR_MERGE",
)


def get_public_profile(db: Session, username: str) -> PublicUserProfile:
    user = _get_user_or_404(db, username)
    return PublicUserProfile(
        id=user.id,
        username=user.username,
        avatar_url=user.avatar_url,
        bio=user.bio,
        created_at=user.created_at,
        pr_count=user_repo.count_user_submitted_prs(db, user.id),
        merged_count=user_repo.count_user_merged_contributions(db, user.id),
        repository_count=user_repo.count_user_repositories(db, user.id),
    )


def update_me(db: Session, user: User, payload: UserProfileUpdateRequest) -> User:
    updates = payload.model_dump(exclude_unset=True)
    if "avatar_url" in updates:
        user.avatar_url = updates["avatar_url"]
    if "bio" in updates:
        user.bio = updates["bio"]
    db.commit()
    db.refresh(user)
    return user


def list_user_repositories(
    db: Session,
    username: str,
    *,
    page: int,
    size: int,
    sort: str,
) -> PageResponse[RepositorySummary]:
    user = _get_user_or_404(db, username)
    page, size = _normalize_pagination(page, size)

    merge_counts = (
        select(Merge.repository_id.label("repository_id"), func.count(Merge.id).label("merge_count"))
        .group_by(Merge.repository_id)
        .subquery()
    )
    pr_counts = (
        select(PullRequest.repository_id.label("repository_id"), func.count(PullRequest.id).label("pr_count"))
        .where(PullRequest.status != PullRequestStatus.DRAFT)
        .group_by(PullRequest.repository_id)
        .subquery()
    )
    base = (
        select(
            Repository,
            func.coalesce(merge_counts.c.merge_count, 0).label("merge_count"),
            func.coalesce(pr_counts.c.pr_count, 0).label("pr_count"),
        )
        .outerjoin(merge_counts, merge_counts.c.repository_id == Repository.id)
        .outerjoin(pr_counts, pr_counts.c.repository_id == Repository.id)
        .where(Repository.author_id == user.id)
    )

    if sort == "latest":
        base = base.order_by(desc(Repository.created_at), desc(Repository.id))
    elif sort == "popular":
        base = base.order_by(desc("merge_count"), desc("pr_count"), desc(Repository.created_at), desc(Repository.id))
    else:
        raise AppError("INVALID_SORT", "Invalid sort value", status_code=400)

    total = user_repo.count_statement(db, base)
    rows = db.execute(base.offset((page - 1) * size).limit(size)).all()
    repo_ids = [row.Repository.id for row in rows]
    tags_by_repo = user_repo.get_repository_tags(db, repo_ids)

    return PageResponse(
        items=[
            RepositorySummary(
                id=row.Repository.id,
                title=row.Repository.title,
                description=row.Repository.description,
                thumbnail_url=row.Repository.thumbnail_url,
                tags=tags_by_repo.get(row.Repository.id, []),
                merge_count=row.merge_count,
                pr_count=row.pr_count,
                created_at=row.Repository.created_at,
            )
            for row in rows
        ],
        total=total,
        page=page,
        size=size,
    )


def list_user_contributions(
    db: Session,
    username: str,
    *,
    grade: ContributionGrade | None,
    page: int,
    size: int,
) -> PageResponse[ContributionSummary]:
    user = _get_user_or_404(db, username)
    page, size = _normalize_pagination(page, size)

    base = (
        select(Merge, PullRequest, Repository)
        .join(PullRequest, PullRequest.id == Merge.pull_request_id)
        .join(Repository, Repository.id == Merge.repository_id)
        .where(Merge.contributor_id == user.id)
    )
    if grade:
        base = base.where(Merge.final_grade == grade)
    base = base.order_by(desc(Merge.merged_at), desc(Merge.id))

    total = user_repo.count_statement(db, base)
    rows = db.execute(base.offset((page - 1) * size).limit(size)).all()

    return PageResponse(
        items=[
            ContributionSummary(
                merge_id=merge.id,
                pull_request=PullRequestNestedSummary(id=pull_request.id, title=pull_request.title),
                repository=RepositoryNestedSummary(id=repository.id, title=repository.title),
                final_grade=merge.final_grade,
                credit_text=merge.credit_text,
                citation_url=merge.citation_url,
                merged_at=merge.merged_at,
            )
            for merge, pull_request, repository in rows
        ],
        total=total,
        page=page,
        size=size,
    )


def list_user_pull_requests(
    db: Session,
    username: str,
    *,
    current_user: User | None,
    statuses: list[PullRequestStatus] | None,
    repository_id: int | None,
    sort: str,
    page: int,
    size: int,
) -> PageResponse[PullRequestSummary]:
    user = _get_user_or_404(db, username)
    page, size = _normalize_pagination(page, size)
    is_self = current_user is not None and current_user.id == user.id
    requested_statuses = statuses or []

    if PullRequestStatus.DRAFT in requested_statuses:
        if not is_self:
            raise AppError("INVALID_STATUS_FILTER", "DRAFT status can be requested only by the owner", status_code=400)
        if len(set(requested_statuses)) > 1:
            raise AppError("INVALID_STATUS_FILTER", "DRAFT status cannot be mixed with other statuses", status_code=400)

    base = (
        select(PullRequest, Repository)
        .join(Repository, Repository.id == PullRequest.repository_id)
        .where(PullRequest.author_id == user.id)
    )
    if repository_id is not None:
        base = base.where(PullRequest.repository_id == repository_id)

    if requested_statuses:
        base = base.where(PullRequest.status.in_(requested_statuses))
    else:
        base = base.where(PullRequest.status != PullRequestStatus.DRAFT)

    if not is_self:
        base = base.where(
            PullRequest.visibility == Visibility.PUBLIC,
            PullRequest.status != PullRequestStatus.DRAFT,
        )

    if sort == "submitted_at_desc":
        base = base.order_by(desc(PullRequest.submitted_at), desc(PullRequest.id))
    elif sort == "first_drafted_at_desc":
        base = base.order_by(desc(PullRequest.first_drafted_at), desc(PullRequest.id))
    else:
        raise AppError("INVALID_SORT", "Invalid sort value", status_code=400)

    total = user_repo.count_statement(db, base)
    rows = db.execute(base.offset((page - 1) * size).limit(size)).all()
    pr_ids = [pull_request.id for pull_request, _ in rows]
    ai_grades = user_repo.get_latest_ai_grades(db, pr_ids)

    return PageResponse(
        items=[
            PullRequestSummary(
                id=pull_request.id,
                repository=RepositoryNestedSummary(id=repository.id, title=repository.title),
                title=pull_request.title,
                status=pull_request.status,
                visibility=pull_request.visibility,
                ai_grade=ai_grades.get(pull_request.id),
                author_grade_override=pull_request.author_grade_override,
                first_drafted_at=pull_request.first_drafted_at,
                last_saved_at=pull_request.last_saved_at,
                submitted_at=pull_request.submitted_at,
            )
            for pull_request, repository in rows
        ],
        total=total,
        page=page,
        size=size,
    )


def get_contributor_stats(db: Session, username: str) -> ContributorStatsResponse:
    user = _get_user_or_404(db, username)

    total_prs = user_repo.count_user_submitted_prs(db, user.id)
    merged_prs = db.scalar(select(func.count(PullRequest.id)).where(
        PullRequest.author_id == user.id,
        PullRequest.status == PullRequestStatus.MERGED,
    )) or 0
    grade_counts = _merge_grade_counts(db, Merge.contributor_id == user.id)
    last_activity_at = db.scalar(select(func.max(PullRequest.submitted_at)).where(
        PullRequest.author_id == user.id,
        PullRequest.status != PullRequestStatus.DRAFT,
    ))

    return ContributorStatsResponse(
        total_prs=total_prs,
        merged_prs=merged_prs,
        major_count=grade_counts[ContributionGrade.MAJOR],
        normal_count=grade_counts[ContributionGrade.NORMAL],
        minor_count=grade_counts[ContributionGrade.MINOR],
        merge_ratio=_ratio(merged_prs, total_prs, digits=2),
        last_activity_at=last_activity_at,
    )


def get_author_stats(db: Session, username: str) -> AuthorStatsResponse:
    user = _get_user_or_404(db, username)
    repository_count = user_repo.count_user_repositories(db, user.id)

    received_prs = db.scalar(
        select(func.count(PullRequest.id))
        .join(Repository, Repository.id == PullRequest.repository_id)
        .where(
            Repository.author_id == user.id,
            PullRequest.status != PullRequestStatus.DRAFT,
        )
    ) or 0
    merged_prs = db.scalar(select(func.count(Merge.id)).where(Merge.author_id == user.id)) or 0
    first_reviews = (
        select(
            AuditLog.target_id.label("pull_request_id"),
            func.min(AuditLog.created_at).label("first_reviewed_at"),
        )
        .where(
            AuditLog.actor_id == user.id,
            AuditLog.target_type == "pull_request",
            AuditLog.action_type.in_(AUTHOR_REVIEW_ACTIONS),
        )
        .group_by(AuditLog.target_id)
        .subquery()
    )
    review_rows = db.execute(
        select(PullRequest.submitted_at, first_reviews.c.first_reviewed_at)
        .join(Repository, Repository.id == PullRequest.repository_id)
        .join(first_reviews, first_reviews.c.pull_request_id == PullRequest.id)
        .where(
            Repository.author_id == user.id,
            PullRequest.status.in_(REVIEWED_STATUSES),
            PullRequest.submitted_at.is_not(None),
        )
    ).all()
    review_days = [
        _days_between(submitted_at, reviewed_at)
        for submitted_at, reviewed_at in review_rows
        if submitted_at and reviewed_at
    ]
    last_activity_at = db.scalar(
        select(func.max(AuditLog.created_at)).where(
            AuditLog.actor_id == user.id,
            AuditLog.target_type == "pull_request",
            AuditLog.action_type.in_(AUTHOR_REVIEW_ACTIONS),
        )
    )

    return AuthorStatsResponse(
        repository_count=repository_count,
        received_prs=received_prs,
        merged_prs=merged_prs,
        merge_ratio=_ratio(merged_prs, received_prs, digits=2),
        avg_review_days=round(sum(review_days) / len(review_days), 1) if review_days else 0.0,
        last_activity_at=last_activity_at,
    )


def get_badges(db: Session, username: str) -> BadgesResponse:
    _get_user_or_404(db, username)
    return BadgesResponse()


def _get_user_or_404(db: Session, username: str) -> User:
    user = user_repo.get_user_by_username(db, username)
    if user is None:
        raise AppError("USER_NOT_FOUND", "User not found", status_code=404)
    return user


def _normalize_pagination(page: int, size: int) -> tuple[int, int]:
    if page < 1:
        raise AppError("INVALID_PAGINATION", "Page must be greater than or equal to 1", status_code=400)
    if size < 1 or size > MAX_PAGE_SIZE:
        raise AppError("INVALID_PAGINATION", f"Size must be between 1 and {MAX_PAGE_SIZE}", status_code=400)
    return page, size


def _merge_grade_counts(db: Session, *where_clause) -> dict[ContributionGrade, int]:
    statement = select(
        func.sum(case((Merge.final_grade == ContributionGrade.MAJOR, 1), else_=0)).label("major"),
        func.sum(case((Merge.final_grade == ContributionGrade.NORMAL, 1), else_=0)).label("normal"),
        func.sum(case((Merge.final_grade == ContributionGrade.MINOR, 1), else_=0)).label("minor"),
    ).where(*where_clause)
    row = db.execute(statement).one()
    return {
        ContributionGrade.MAJOR: row.major or 0,
        ContributionGrade.NORMAL: row.normal or 0,
        ContributionGrade.MINOR: row.minor or 0,
    }


def _ratio(numerator: int, denominator: int, *, digits: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, digits)


def _days_between(start: datetime, end: datetime) -> float:
    return (end - start).total_seconds() / 86400
