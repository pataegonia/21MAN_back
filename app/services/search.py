from sqlalchemy import case, desc, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import AppError
from app.models.enums import PullRequestStatus
from app.models.merge import Merge
from app.models.pull_request import PullRequest
from app.models.repository import RecruitingArea, Repository, RepositoryTag, Tag
from app.models.user import User
from app.repositories import repositories as repo_repo
from app.schemas.repositories import RecruitingAreaSlug, RepositoryListItem
from app.schemas.search import (
    SearchResponse,
    SearchSort,
    SearchType,
    UserRole,
    UserSearchItem,
    UserSearchSection,
    RepositorySearchSection,
)
from app.services.repositories import _to_list_item

MAX_PAGE_SIZE = 100


def search(
    db: Session,
    *,
    q: str | None,
    search_type: SearchType,
    sort: SearchSort,
    tags: list[str] | None,
    author: str | None,
    recruiting: RecruitingAreaSlug | None,
    role: UserRole | None,
    page: int,
    size: int,
) -> SearchResponse:
    page, size = _normalize_pagination(page, size)
    normalized_q = q.strip() if q else None

    repositories = RepositorySearchSection(items=[], total=0)
    users = UserSearchSection(items=[], total=0)

    if search_type in (SearchType.ALL, SearchType.REPOSITORY):
        repositories = _search_repositories(
            db,
            q=normalized_q,
            tags=tags,
            author=author,
            recruiting=recruiting,
            sort=sort,
            page=page,
            size=size,
        )

    if search_type in (SearchType.ALL, SearchType.USER):
        users = _search_users(
            db,
            q=normalized_q,
            role=role,
            sort=sort,
            page=page,
            size=size,
        )

    return SearchResponse(repositories=repositories, users=users, page=page, size=size)


def _search_repositories(
    db: Session,
    *,
    q: str | None,
    tags: list[str] | None,
    author: str | None,
    recruiting: RecruitingAreaSlug | None,
    sort: SearchSort,
    page: int,
    size: int,
) -> RepositorySearchSection:
    merge_counts, pr_counts = _repository_count_subqueries()
    statement = (
        select(
            Repository,
            func.coalesce(merge_counts.c.merge_count, 0).label("merge_count"),
            func.coalesce(pr_counts.c.pr_count, 0).label("pr_count"),
        )
        .options(
            selectinload(Repository.author),
            selectinload(Repository.tags).selectinload(RepositoryTag.tag),
            selectinload(Repository.recruiting_areas),
        )
        .outerjoin(merge_counts, merge_counts.c.repository_id == Repository.id)
        .outerjoin(pr_counts, pr_counts.c.repository_id == Repository.id)
    )

    if q:
        keyword = f"%{q}%"
        statement = statement.where(or_(Repository.title.ilike(keyword), Repository.description.ilike(keyword)))

    if author:
        statement = statement.join(User, User.id == Repository.author_id).where(func.lower(User.username) == author.lower())

    if tags:
        for tag in tags:
            cleaned = tag.strip().lower()
            if not cleaned:
                continue
            statement = statement.where(
                Repository.id.in_(
                    select(RepositoryTag.repository_id)
                    .join(Tag, Tag.id == RepositoryTag.tag_id)
                    .where(func.lower(Tag.name) == cleaned)
                )
            )

    if recruiting:
        statement = statement.where(
            Repository.id.in_(
                select(RecruitingArea.repository_id).where(
                    RecruitingArea.name == recruiting.value,
                    RecruitingArea.is_active.is_(True),
                )
            )
        )

    if sort == SearchSort.POPULAR:
        statement = statement.order_by(desc("merge_count"), desc("pr_count"), desc(Repository.created_at), desc(Repository.id))
    else:
        statement = statement.order_by(desc(Repository.created_at), desc(Repository.id))

    total = _count_statement(db, statement)
    rows = db.execute(statement.offset((page - 1) * size).limit(size)).all()
    items = [_to_list_item(row.Repository, row.pr_count, row.merge_count) for row in rows]
    return RepositorySearchSection(items=items, total=total)


def _search_users(
    db: Session,
    *,
    q: str | None,
    role: UserRole | None,
    sort: SearchSort,
    page: int,
    size: int,
) -> UserSearchSection:
    total_prs, merged_prs, repo_counts, last_activity = _user_stat_subqueries()
    statement = (
        select(
            User,
            func.coalesce(total_prs.c.total_prs, 0).label("total_prs"),
            func.coalesce(merged_prs.c.merged_prs, 0).label("merged_prs"),
            func.coalesce(repo_counts.c.repository_count, 0).label("repository_count"),
            last_activity.c.last_activity_at.label("last_activity_at"),
        )
        .outerjoin(total_prs, total_prs.c.user_id == User.id)
        .outerjoin(merged_prs, merged_prs.c.user_id == User.id)
        .outerjoin(repo_counts, repo_counts.c.user_id == User.id)
        .outerjoin(last_activity, last_activity.c.user_id == User.id)
    )

    if q:
        statement = statement.where(User.username.ilike(f"%{q}%"))

    if role == UserRole.AUTHOR:
        statement = statement.where(func.coalesce(repo_counts.c.repository_count, 0) > 0)
    elif role == UserRole.CONTRIBUTOR:
        statement = statement.where(func.coalesce(total_prs.c.total_prs, 0) > 0)

    if sort == SearchSort.POPULAR:
        statement = statement.order_by(desc("merged_prs"), desc("total_prs"), desc(User.created_at), desc(User.id))
    else:
        statement = statement.order_by(
            case((last_activity.c.last_activity_at.is_(None), 1), else_=0),
            desc(last_activity.c.last_activity_at),
            desc(User.created_at),
            desc(User.id),
        )

    total = _count_statement(db, statement)
    rows = db.execute(statement.offset((page - 1) * size).limit(size)).all()
    return UserSearchSection(
        items=[
            UserSearchItem(
                id=user.id,
                username=user.username,
                avatar_url=user.avatar_url,
                bio=user.bio,
                merged_prs=merged_count or 0,
                total_prs=total_count or 0,
            )
            for user, total_count, merged_count, _, _ in rows
        ],
        total=total,
    )


def _repository_count_subqueries():
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
    return merge_counts, pr_counts


def _user_stat_subqueries():
    total_prs = (
        select(PullRequest.author_id.label("user_id"), func.count(PullRequest.id).label("total_prs"))
        .where(PullRequest.status != PullRequestStatus.DRAFT)
        .group_by(PullRequest.author_id)
        .subquery()
    )
    merged_prs = (
        select(PullRequest.author_id.label("user_id"), func.count(PullRequest.id).label("merged_prs"))
        .where(PullRequest.status == PullRequestStatus.MERGED)
        .group_by(PullRequest.author_id)
        .subquery()
    )
    repo_counts = (
        select(Repository.author_id.label("user_id"), func.count(Repository.id).label("repository_count"))
        .group_by(Repository.author_id)
        .subquery()
    )
    last_activity = (
        select(PullRequest.author_id.label("user_id"), func.max(PullRequest.submitted_at).label("last_activity_at"))
        .where(PullRequest.status != PullRequestStatus.DRAFT)
        .group_by(PullRequest.author_id)
        .subquery()
    )
    return total_prs, merged_prs, repo_counts, last_activity


def _count_statement(db: Session, statement) -> int:
    return db.scalar(select(func.count()).select_from(statement.order_by(None).subquery())) or 0


def _normalize_pagination(page: int, size: int) -> tuple[int, int]:
    if page < 1:
        raise AppError("INVALID_PAGINATION", "Page must be greater than or equal to 1", 400)
    if size < 1 or size > MAX_PAGE_SIZE:
        raise AppError("INVALID_PAGINATION", f"Size must be between 1 and {MAX_PAGE_SIZE}", 400)
    return page, size
