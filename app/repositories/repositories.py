import re
import secrets

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, selectinload

from app.models.ai_analysis import AiAnalysis
from app.models.repository import RecruitingArea, Repository, RepositoryTag, Tag


_SLUG_REPLACE = re.compile(r"[^a-z0-9가-힣]+")
_SLUG_MAX_BASE = 180


def _repository_eager_load_options() -> list:
    return [
        selectinload(Repository.author),
        selectinload(Repository.characters),
        selectinload(Repository.regions),
        selectinload(Repository.rules),
        selectinload(Repository.forbidden_items),
        selectinload(Repository.recruiting_areas),
        selectinload(Repository.tags).selectinload(RepositoryTag.tag),
    ]


def get_repository_by_id(db: Session, repo_id: int) -> Repository | None:
    return db.get(Repository, repo_id, options=_repository_eager_load_options())


def get_repository_by_slug(db: Session, slug: str) -> Repository | None:
    statement = select(Repository).where(Repository.slug == slug).options(*_repository_eager_load_options())
    return db.scalar(statement)


def get_repository_by_ref(db: Session, ref: int | str) -> Repository | None:
    if isinstance(ref, int):
        return get_repository_by_id(db, ref)
    text = ref.strip()
    if text.isdigit():
        return get_repository_by_id(db, int(text))
    return get_repository_by_slug(db, text)


def generate_unique_slug(db: Session, title: str) -> str:
    base = _SLUG_REPLACE.sub("-", title.strip().lower()).strip("-")
    if not base:
        base = "repo"
    base = base[:_SLUG_MAX_BASE]
    for _ in range(8):
        candidate = f"{base}-{secrets.token_hex(4)}"
        if db.scalar(select(Repository.id).where(Repository.slug == candidate)) is None:
            return candidate
    raise RuntimeError("Failed to generate unique repository slug")


def get_or_create_tag(db: Session, name: str) -> Tag:
    statement = select(Tag).where(func.lower(Tag.name) == name.lower())
    tag = db.scalar(statement)
    if tag is not None:
        return tag
    tag = Tag(name=name)
    db.add(tag)
    db.flush()
    return tag


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


def count_statement(db: Session, statement: Select) -> int:
    return db.scalar(select(func.count()).select_from(statement.subquery())) or 0


def recruiting_slugs(repository: Repository) -> list[str]:
    return [
        area.name
        for area in sorted(repository.recruiting_areas, key=lambda item: item.order_index)
        if area.is_active
    ]
