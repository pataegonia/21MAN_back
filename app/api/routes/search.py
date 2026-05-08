from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.repositories import RecruitingAreaSlug
from app.schemas.search import SearchResponse, SearchSort, SearchType, UserRole
from app.services import search as search_service

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse)
def search(
    q: str | None = None,
    search_type: SearchType = Query(default=SearchType.ALL, alias="type"),
    sort: SearchSort = SearchSort.LATEST,
    tag: Annotated[list[str] | None, Query()] = None,
    author: str | None = None,
    recruiting: RecruitingAreaSlug | None = None,
    role: UserRole | None = None,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> SearchResponse:
    return search_service.search(
        db,
        q=q,
        search_type=search_type,
        sort=sort,
        tags=tag,
        author=author,
        recruiting=recruiting,
        role=role,
        page=page,
        size=size,
    )
