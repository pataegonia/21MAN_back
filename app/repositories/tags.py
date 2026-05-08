from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.repository import RepositoryTag, Tag


def search_tags(db: Session, q: str | None, size: int) -> list[Tag]:
    stmt = select(Tag)
    if q:
        stmt = stmt.where(Tag.name.like(f"%{q}%"))
    stmt = stmt.order_by(Tag.name).limit(size)
    return list(db.scalars(stmt))


def get_popular_tags(db: Session, size: int) -> list[tuple[Tag, int]]:
    stmt = (
        select(Tag, func.count(RepositoryTag.repository_id).label("repo_count"))
        .join(RepositoryTag, Tag.id == RepositoryTag.tag_id)
        .group_by(Tag.id)
        .order_by(func.count(RepositoryTag.repository_id).desc())
        .limit(size)
    )
    return list(db.execute(stmt))
