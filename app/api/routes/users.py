from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_user_optional
from app.db.session import get_db
from app.models.enums import ContributionGrade, PullRequestStatus
from app.models.user import User
from app.schemas.users import (
    AuthorStatsResponse,
    BadgesResponse,
    ContributionSummary,
    ContributorStatsResponse,
    PageResponse,
    PublicUserProfile,
    PullRequestSummary,
    RepositorySummary,
    UserProfileUpdateRequest,
    UserProfileUpdateResponse,
)
from app.services import users as user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/me", response_model=UserProfileUpdateResponse)
def update_me(
    payload: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    return user_service.update_me(db, current_user, payload)


@router.get("/{username}", response_model=PublicUserProfile)
def get_user_profile(username: str, db: Session = Depends(get_db)) -> PublicUserProfile:
    return user_service.get_public_profile(db, username)


@router.get("/{username}/repositories", response_model=PageResponse[RepositorySummary])
def get_user_repositories(
    username: str,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    sort: str = Query(default="latest", pattern="^(latest|popular)$"),
    db: Session = Depends(get_db),
) -> PageResponse[RepositorySummary]:
    return user_service.list_user_repositories(db, username, page=page, size=size, sort=sort)


@router.get("/{username}/contributions", response_model=PageResponse[ContributionSummary])
def get_user_contributions(
    username: str,
    grade: ContributionGrade | None = None,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PageResponse[ContributionSummary]:
    return user_service.list_user_contributions(db, username, grade=grade, page=page, size=size)


@router.get("/{username}/pull-requests", response_model=PageResponse[PullRequestSummary])
def get_user_pull_requests(
    username: str,
    status: Annotated[list[PullRequestStatus] | None, Query()] = None,
    repository_id: int | None = None,
    sort: str = Query(default="submitted_at_desc", pattern="^(submitted_at_desc|first_drafted_at_desc)$"),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    current_user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
) -> PageResponse[PullRequestSummary]:
    return user_service.list_user_pull_requests(
        db,
        username,
        current_user=current_user,
        statuses=status,
        repository_id=repository_id,
        sort=sort,
        page=page,
        size=size,
    )


@router.get("/{username}/stats/contributor", response_model=ContributorStatsResponse)
def get_contributor_stats(username: str, db: Session = Depends(get_db)) -> ContributorStatsResponse:
    return user_service.get_contributor_stats(db, username)


@router.get("/{username}/stats/author", response_model=AuthorStatsResponse)
def get_author_stats(username: str, db: Session = Depends(get_db)) -> AuthorStatsResponse:
    return user_service.get_author_stats(db, username)


@router.get("/{username}/badges", response_model=BadgesResponse)
def get_user_badges(username: str, db: Session = Depends(get_db)) -> BadgesResponse:
    return user_service.get_badges(db, username)
