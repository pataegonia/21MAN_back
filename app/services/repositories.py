from datetime import UTC, datetime

from sqlalchemy import case, desc, func, or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.audit_log import AuditLog
from app.models.enums import ContributionGrade, PullRequestStatus, Visibility
from app.models.merge import Merge
from app.models.pull_request import PullRequest
from app.models.repository import (
    RecruitingArea,
    RepoCharacter,
    RepoForbidden,
    RepoRegion,
    RepoRule,
    Repository,
    RepositoryTag,
    Tag,
)
from app.models.user import User
from app.repositories import repositories as repo_repo
from app.schemas.repositories import (
    ContributorSummary,
    ExternalLink,
    MergeSummary,
    PageResponse,
    PullRequestListItem,
    ReadmeNamedItem,
    ReadmeResponse,
    RecruitingAreaSlug,
    RepositoryCreateRequest,
    RepositoryDetailResponse,
    RepositoryListItem,
    RepositoryNestedSummary,
    RepositoryStatsResponse,
    RepositoryUpdateRequest,
    UserSummary,
)

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


def create_repository(db: Session, *, author: User, payload: RepositoryCreateRequest) -> RepositoryDetailResponse:
    slug = repo_repo.generate_unique_slug(db, payload.title)
    repo = Repository(
        author_id=author.id,
        slug=slug,
        title=payload.title,
        description=payload.description,
        thumbnail_url=payload.thumbnail_url,
        external_links=[link.model_dump(mode="json") for link in payload.external_links],
        readme_overview=payload.readme.overview if payload.readme else None,
        contribution_guideline=payload.contribution_guidelines,
    )
    db.add(repo)
    db.flush()

    _replace_tags(db, repo, payload.tags)
    if payload.readme:
        _replace_readme_children(db, repo, payload.readme.model_dump(exclude_unset=True))
    _replace_recruiting_areas(db, repo, payload.recruiting_areas)

    db.commit()
    return get_repository_detail(db, repo.id)


def list_repositories(
    db: Session,
    *,
    q: str | None,
    tag: list[str] | None,
    recruiting: RecruitingAreaSlug | None,
    sort: str,
    page: int,
    size: int,
) -> PageResponse[RepositoryListItem]:
    page, size = _normalize_pagination(page, size)
    merge_counts, pr_counts = _count_subqueries()
    base = _repository_list_base(merge_counts, pr_counts)

    if q:
        keyword = f"%{q.strip()}%"
        base = base.where(or_(Repository.title.ilike(keyword), Repository.description.ilike(keyword)))

    if tag:
        for tag_value in tag:
            cleaned = tag_value.strip().lower()
            base = base.where(
                Repository.id.in_(
                    select(RepositoryTag.repository_id)
                    .join(Tag, Tag.id == RepositoryTag.tag_id)
                    .where(func.lower(Tag.name) == cleaned)
                )
            )

    if recruiting:
        base = base.where(
            Repository.id.in_(
                select(RecruitingArea.repository_id).where(
                    RecruitingArea.name == recruiting.value,
                    RecruitingArea.is_active.is_(True),
                )
            )
        )

    base = _apply_repository_sort(base, sort)
    total = repo_repo.count_statement(db, base)
    rows = db.execute(base.offset((page - 1) * size).limit(size)).all()

    return PageResponse(
        items=[_to_list_item(row.Repository, row.pr_count, row.merge_count) for row in rows],
        total=total,
        page=page,
        size=size,
    )


def get_repository_detail(db: Session, repo_ref: int | str) -> RepositoryDetailResponse:
    repo = _get_repo_or_404(db, repo_ref)
    return _to_detail_response(db, repo)


def update_repository(
    db: Session,
    *,
    repo_ref: int | str,
    user: User,
    payload: RepositoryUpdateRequest,
) -> RepositoryDetailResponse:
    repo = _get_repo_or_404(db, repo_ref)
    _ensure_repo_owner(repo, user)
    updates = payload.model_dump(exclude_unset=True)

    for field_name in ("title", "description", "thumbnail_url"):
        if field_name in updates:
            setattr(repo, field_name, updates[field_name])
    if "external_links" in updates:
        repo.external_links = [ExternalLink(**link).model_dump(mode="json") for link in updates["external_links"]]
    if "contribution_guidelines" in updates:
        repo.contribution_guideline = updates["contribution_guidelines"]
    if "tags" in updates:
        _replace_tags(db, repo, updates["tags"])
    if "recruiting_areas" in updates:
        _replace_recruiting_areas(db, repo, updates["recruiting_areas"])
    if "readme" in updates and updates["readme"] is not None:
        readme_updates = updates["readme"]
        if "overview" in readme_updates:
            repo.readme_overview = readme_updates["overview"]
        _replace_readme_children(db, repo, readme_updates)

    if updates:
        db.add(
            AuditLog(
                actor_id=user.id,
                action_type="REPO_UPDATE",
                target_type="repository",
                target_id=repo.id,
                payload={"updated_fields": sorted(updates.keys())},
                created_at=_now(),
            )
        )

    db.commit()
    return get_repository_detail(db, repo.id)


def list_contributors(db: Session, repo_ref: int | str, *, page: int, size: int) -> PageResponse[ContributorSummary]:
    repo = _get_repo_or_404(db, repo_ref)
    page, size = _normalize_pagination(page, size)

    statement = (
        select(
            User,
            func.count(Merge.id).label("merge_count"),
            func.sum(case((Merge.final_grade == ContributionGrade.MAJOR, 1), else_=0)).label("major_count"),
            func.sum(case((Merge.final_grade == ContributionGrade.NORMAL, 1), else_=0)).label("normal_count"),
            func.sum(case((Merge.final_grade == ContributionGrade.MINOR, 1), else_=0)).label("minor_count"),
            func.max(Merge.merged_at).label("last_merged_at"),
        )
        .join(Merge, Merge.contributor_id == User.id)
        .where(Merge.repository_id == repo.id)
        .group_by(User.id)
        .order_by(desc("merge_count"), desc("last_merged_at"))
    )
    total = repo_repo.count_statement(db, statement)
    rows = db.execute(statement.offset((page - 1) * size).limit(size)).all()

    return PageResponse(
        items=[
            ContributorSummary(
                user=_user_summary(user),
                merge_count=merge_count or 0,
                major_count=major_count or 0,
                normal_count=normal_count or 0,
                minor_count=minor_count or 0,
                last_merged_at=last_merged_at,
            )
            for user, merge_count, major_count, normal_count, minor_count, last_merged_at in rows
        ],
        total=total,
        page=page,
        size=size,
    )


def list_merges(db: Session, repo_ref: int | str, *, page: int, size: int) -> PageResponse[MergeSummary]:
    repo = _get_repo_or_404(db, repo_ref)
    page, size = _normalize_pagination(page, size)

    statement = (
        select(Merge, User)
        .join(User, User.id == Merge.contributor_id)
        .where(Merge.repository_id == repo.id)
        .order_by(desc(Merge.merged_at), desc(Merge.id))
    )
    total = repo_repo.count_statement(db, statement)
    rows = db.execute(statement.offset((page - 1) * size).limit(size)).all()

    return PageResponse(
        items=[
            MergeSummary(
                id=merge.id,
                pull_request_id=merge.pull_request_id,
                contributor=_user_summary(contributor),
                final_grade=merge.final_grade,
                credit_text=merge.credit_text,
                citation_url=merge.citation_url,
                merged_at=merge.merged_at,
            )
            for merge, contributor in rows
        ],
        total=total,
        page=page,
        size=size,
    )


def list_repository_pull_requests(
    db: Session,
    repo_ref: int | str,
    *,
    current_user: User | None,
    statuses: list[PullRequestStatus] | None,
    page: int,
    size: int,
) -> PageResponse[PullRequestListItem]:
    repo = _get_repo_or_404(db, repo_ref)
    page, size = _normalize_pagination(page, size)

    if statuses and PullRequestStatus.DRAFT in statuses:
        raise AppError("INVALID_STATUS_FILTER", "DRAFT pull requests are not available in repository PR lists", 400)

    is_owner = current_user is not None and current_user.id == repo.author_id
    statement = (
        select(PullRequest, User)
        .join(User, User.id == PullRequest.author_id)
        .where(
            PullRequest.repository_id == repo.id,
            PullRequest.status != PullRequestStatus.DRAFT,
        )
    )
    if statuses:
        statement = statement.where(PullRequest.status.in_(statuses))
    if not is_owner:
        statement = statement.where(PullRequest.visibility == Visibility.PUBLIC)
    statement = statement.order_by(desc(PullRequest.submitted_at), desc(PullRequest.id))

    total = repo_repo.count_statement(db, statement)
    rows = db.execute(statement.offset((page - 1) * size).limit(size)).all()
    pr_ids = [pull_request.id for pull_request, _ in rows]
    ai_grades = repo_repo.get_latest_ai_grades(db, pr_ids)

    return PageResponse(
        items=[
            PullRequestListItem(
                id=pull_request.id,
                repository=RepositoryNestedSummary(id=repo.id, title=repo.title),
                author=_user_summary(author),
                title=pull_request.title,
                status=pull_request.status,
                visibility=pull_request.visibility,
                ai_grade=ai_grades.get(pull_request.id),
                author_grade_override=pull_request.author_grade_override,
                first_drafted_at=pull_request.first_drafted_at,
                last_saved_at=pull_request.last_saved_at,
                submitted_at=pull_request.submitted_at,
            )
            for pull_request, author in rows
        ],
        total=total,
        page=page,
        size=size,
    )


def get_repository_stats(db: Session, repo_ref: int | str, *, user: User) -> RepositoryStatsResponse:
    repo = _get_repo_or_404(db, repo_ref)
    _ensure_repo_owner(repo, user)

    counts = db.execute(
        select(
            func.sum(case((PullRequest.status != PullRequestStatus.DRAFT, 1), else_=0)).label("received_prs"),
            func.sum(case((PullRequest.status == PullRequestStatus.MERGED, 1), else_=0)).label("merged_prs"),
            func.sum(case((PullRequest.status == PullRequestStatus.SUBMITTED, 1), else_=0)).label("awaiting_review_prs"),
            func.sum(case((PullRequest.status == PullRequestStatus.ACCEPTED, 1), else_=0)).label("awaiting_merge_prs"),
            func.sum(case((PullRequest.status == PullRequestStatus.CHANGES_REQUESTED, 1), else_=0)).label("awaiting_resubmit_prs"),
            func.sum(case((PullRequest.status == PullRequestStatus.REJECTED, 1), else_=0)).label("rejected_prs"),
        ).where(PullRequest.repository_id == repo.id)
    ).one()

    received_prs = counts.received_prs or 0
    merged_prs = counts.merged_prs or 0
    return RepositoryStatsResponse(
        repository_id=repo.id,
        received_prs=received_prs,
        merged_prs=merged_prs,
        merge_ratio=round(merged_prs / received_prs, 2) if received_prs else 0.0,
        awaiting_review_prs=counts.awaiting_review_prs or 0,
        awaiting_merge_prs=counts.awaiting_merge_prs or 0,
        awaiting_resubmit_prs=counts.awaiting_resubmit_prs or 0,
        rejected_prs=counts.rejected_prs or 0,
    )


def _get_repo_or_404(db: Session, repo_ref: int | str) -> Repository:
    repo = repo_repo.get_repository_by_ref(db, repo_ref)
    if repo is None:
        raise AppError("REPOSITORY_NOT_FOUND", "Repository not found", 404)
    return repo


def _ensure_repo_owner(repo: Repository, user: User) -> None:
    if repo.author_id != user.id:
        raise AppError("FORBIDDEN", "Only the repository author can perform this action", 403)


def _normalize_pagination(page: int, size: int) -> tuple[int, int]:
    if page < 1:
        raise AppError("INVALID_PAGINATION", "Page must be greater than or equal to 1", 400)
    if size < 1 or size > MAX_PAGE_SIZE:
        raise AppError("INVALID_PAGINATION", f"Size must be between 1 and {MAX_PAGE_SIZE}", 400)
    return page, size


def _count_subqueries():
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


def _repository_list_base(merge_counts, pr_counts):
    return (
        select(
            Repository,
            func.coalesce(merge_counts.c.merge_count, 0).label("merge_count"),
            func.coalesce(pr_counts.c.pr_count, 0).label("pr_count"),
        )
        .join(Repository.author)
        .outerjoin(merge_counts, merge_counts.c.repository_id == Repository.id)
        .outerjoin(pr_counts, pr_counts.c.repository_id == Repository.id)
    )


def _apply_repository_sort(statement, sort: str):
    if sort == "latest":
        return statement.order_by(desc(Repository.created_at), desc(Repository.id))
    if sort == "popular":
        return statement.order_by(desc("merge_count"), desc("pr_count"), desc(Repository.created_at), desc(Repository.id))
    raise AppError("INVALID_SORT", "Invalid sort value", 400)


def _replace_tags(db: Session, repo: Repository, tags: list[str]) -> None:
    repo.tags.clear()
    db.flush()
    for tag_name in tags:
        tag = repo_repo.get_or_create_tag(db, tag_name)
        repo.tags.append(RepositoryTag(repository_id=repo.id, tag_id=tag.id))


def _replace_recruiting_areas(db: Session, repo: Repository, areas: list[RecruitingAreaSlug | str]) -> None:
    repo.recruiting_areas.clear()
    db.flush()
    for index, area in enumerate(areas):
        slug = area.value if isinstance(area, RecruitingAreaSlug) else str(area)
        repo.recruiting_areas.append(
            RecruitingArea(
                repository_id=repo.id,
                name=slug,
                content="",
                order_index=index,
                is_active=True,
            )
        )


def _replace_readme_children(db: Session, repo: Repository, readme_updates: dict) -> None:
    if "characters" in readme_updates and readme_updates["characters"] is not None:
        repo.characters.clear()
        db.flush()
        for index, item in enumerate(readme_updates["characters"]):
            repo.characters.append(
                RepoCharacter(
                    repository_id=repo.id,
                    name=item["name"],
                    content=item.get("description") or "",
                    order_index=index,
                )
            )
    if "regions" in readme_updates and readme_updates["regions"] is not None:
        repo.regions.clear()
        db.flush()
        for index, item in enumerate(readme_updates["regions"]):
            repo.regions.append(
                RepoRegion(
                    repository_id=repo.id,
                    name=item["name"],
                    content=item.get("description") or "",
                    order_index=index,
                )
            )
    if "world_rules" in readme_updates and readme_updates["world_rules"] is not None:
        repo.rules.clear()
        db.flush()
        for index, content in enumerate(readme_updates["world_rules"]):
            repo.rules.append(RepoRule(repository_id=repo.id, content=content, order_index=index))
    if "forbidden_settings" in readme_updates and readme_updates["forbidden_settings"] is not None:
        repo.forbidden_items.clear()
        db.flush()
        for index, content in enumerate(readme_updates["forbidden_settings"]):
            repo.forbidden_items.append(RepoForbidden(repository_id=repo.id, content=content, order_index=index))


def _to_detail_response(db: Session, repo: Repository) -> RepositoryDetailResponse:
    merge_counts, pr_counts = _count_subqueries()
    counts = db.execute(
        select(
            func.coalesce(merge_counts.c.merge_count, 0).label("merge_count"),
            func.coalesce(pr_counts.c.pr_count, 0).label("pr_count"),
        )
        .select_from(Repository)
        .outerjoin(merge_counts, merge_counts.c.repository_id == Repository.id)
        .outerjoin(pr_counts, pr_counts.c.repository_id == Repository.id)
        .where(Repository.id == repo.id)
    ).one()
    return RepositoryDetailResponse(
        id=repo.id,
        slug=repo.slug,
        title=repo.title,
        description=repo.description,
        thumbnail_url=repo.thumbnail_url,
        thumbnail=repo.thumbnail_url,
        tags=[repo_tag.tag.name for repo_tag in repo.tags],
        external_links=[ExternalLink(**link) for link in (repo.external_links or [])],
        readme=ReadmeResponse(
            overview=repo.readme_overview,
            content=repo.readme_overview,
            characters=[
                ReadmeNamedItem(name=item.name, description=item.content)
                for item in sorted(repo.characters, key=lambda item: item.order_index)
            ],
            regions=[
                ReadmeNamedItem(name=item.name, description=item.content)
                for item in sorted(repo.regions, key=lambda item: item.order_index)
            ],
            world_rules=[item.content for item in sorted(repo.rules, key=lambda item: item.order_index)],
            forbidden_settings=[
                item.content for item in sorted(repo.forbidden_items, key=lambda item: item.order_index)
            ],
        ),
        recruiting_areas=repo_repo.recruiting_slugs(repo),
        contribution_guidelines=repo.contribution_guideline,
        author=_user_summary(repo.author),
        pr_count=counts.pr_count,
        merge_count=counts.merge_count,
        created_at=repo.created_at,
        updated_at=repo.updated_at,
    )


def _to_list_item(repo: Repository, pr_count: int, merge_count: int) -> RepositoryListItem:
    return RepositoryListItem(
        id=repo.id,
        slug=repo.slug,
        title=repo.title,
        description=repo.description,
        thumbnail_url=repo.thumbnail_url,
        thumbnail=repo.thumbnail_url,
        tags=[repo_tag.tag.name for repo_tag in repo.tags],
        author=_user_summary(repo.author),
        recruiting_areas=repo_repo.recruiting_slugs(repo),
        pr_count=pr_count,
        merge_count=merge_count,
        created_at=repo.created_at,
        updated_at=repo.updated_at,
    )


def _user_summary(user: User) -> UserSummary:
    return UserSummary(id=user.id, username=user.username, avatar_url=user.avatar_url)


def _now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)
