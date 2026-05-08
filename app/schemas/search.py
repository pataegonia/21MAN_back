from enum import StrEnum

from pydantic import BaseModel

from app.schemas.repositories import RepositoryListItem


class SearchType(StrEnum):
    ALL = "all"
    REPOSITORY = "repository"
    USER = "user"


class SearchSort(StrEnum):
    LATEST = "latest"
    POPULAR = "popular"


class UserRole(StrEnum):
    AUTHOR = "author"
    CONTRIBUTOR = "contributor"


class UserSearchItem(BaseModel):
    id: int
    username: str
    avatar_url: str | None
    bio: str | None
    merged_prs: int
    total_prs: int


class RepositorySearchSection(BaseModel):
    items: list[RepositoryListItem]
    total: int


class UserSearchSection(BaseModel):
    items: list[UserSearchItem]
    total: int


class SearchResponse(BaseModel):
    repositories: RepositorySearchSection
    users: UserSearchSection
    page: int
    size: int
