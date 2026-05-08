from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_user_optional
from app.db.session import get_db
from app.models.enums import PullRequestStatus
from app.models.user import User
from app.schemas.repositories import (
    ContributorSummary,
    MergeSummary,
    PageResponse,
    PullRequestListItem,
    RecruitingAreaSlug,
    RepositoryCreateRequest,
    RepositoryDetailResponse,
    RepositoryListItem,
    RepositoryStatsResponse,
    RepositoryUpdateRequest,
)
from app.services import repositories as repo_service

router = APIRouter(prefix="/repositories", tags=["repositories"])


@router.post("", response_model=RepositoryDetailResponse, status_code=status.HTTP_201_CREATED)
def create_repository(
    payload: RepositoryCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RepositoryDetailResponse:
    return repo_service.create_repository(db, author=current_user, payload=payload)


@router.get("", response_model=PageResponse[RepositoryListItem])
def list_repositories(
    q: str | None = None,
    tag: Annotated[list[str] | None, Query()] = None,
    recruiting: RecruitingAreaSlug | None = None,
    sort: str = Query(default="latest", pattern="^(latest|popular)$"),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PageResponse[RepositoryListItem]:
    return repo_service.list_repositories(
        db,
        q=q,
        tag=tag,
        recruiting=recruiting,
        sort=sort,
        page=page,
        size=size,
    )


@router.get("/{repo_id}", response_model=RepositoryDetailResponse)
def get_repository(repo_id: str, db: Session = Depends(get_db)) -> RepositoryDetailResponse:
    return repo_service.get_repository_detail(db, repo_id)


@router.patch("/{repo_id}", response_model=RepositoryDetailResponse)
def update_repository(
    repo_id: str,
    payload: RepositoryUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RepositoryDetailResponse:
    return repo_service.update_repository(db, repo_ref=repo_id, user=current_user, payload=payload)


@router.get("/{repo_id}/contributors", response_model=PageResponse[ContributorSummary])
def get_repository_contributors(
    repo_id: str,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PageResponse[ContributorSummary]:
    return repo_service.list_contributors(db, repo_id, page=page, size=size)


@router.get("/{repo_id}/merges", response_model=PageResponse[MergeSummary])
def get_repository_merges(
    repo_id: str,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PageResponse[MergeSummary]:
    return repo_service.list_merges(db, repo_id, page=page, size=size)


@router.get("/{repo_id}/pull-requests", response_model=PageResponse[PullRequestListItem])
def get_repository_pull_requests(
    repo_id: str,
    status: Annotated[list[PullRequestStatus] | None, Query()] = None,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    current_user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
) -> PageResponse[PullRequestListItem]:
    return repo_service.list_repository_pull_requests(
        db,
        repo_id,
        current_user=current_user,
        statuses=status,
        page=page,
        size=size,
    )


@router.get("/{repo_id}/stats", response_model=RepositoryStatsResponse)
def get_repository_stats(
    repo_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RepositoryStatsResponse:
    return repo_service.get_repository_stats(db, repo_id, user=current_user)
