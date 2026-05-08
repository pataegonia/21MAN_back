from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories import tags as tags_repo
from app.schemas.tags import PopularTagInfo, PopularTagListResponse, TagInfo, TagListResponse

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/popular", response_model=PopularTagListResponse)
def get_popular_tags(
    size: int = Query(default=20, ge=1, le=50),
    db: Session = Depends(get_db),
) -> PopularTagListResponse:
    rows = tags_repo.get_popular_tags(db, size)
    return PopularTagListResponse(
        tags=[PopularTagInfo(id=tag.id, name=tag.name, repository_count=cnt) for tag, cnt in rows]
    )


@router.get("", response_model=TagListResponse)
def search_tags(
    q: str | None = None,
    size: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> TagListResponse:
    tags = tags_repo.search_tags(db, q=q, size=size)
    return TagListResponse(tags=[TagInfo(id=t.id, name=t.name) for t in tags])
