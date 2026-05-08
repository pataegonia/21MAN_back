from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from app.models.enums import ContributionGrade, PullRequestStatus, Visibility
from app.schemas.auth import format_utc

T = TypeVar("T")


class PageResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int


class PublicUserProfile(BaseModel):
    id: int
    username: str
    avatar_url: str | None
    bio: str | None
    created_at: datetime
    pr_count: int
    merged_count: int
    repository_count: int

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        return format_utc(value)


class UserProfileUpdateRequest(BaseModel):
    avatar_url: str | None = Field(default=None, max_length=500)
    bio: str | None = Field(default=None, max_length=500)

    @field_validator("avatar_url", "bio")
    @classmethod
    def normalize_empty_string(cls, value: str | None) -> str | None:
        if value == "":
            return None
        return value


class UserProfileUpdateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    avatar_url: str | None
    bio: str | None


class RepositorySummary(BaseModel):
    id: int
    title: str
    description: str | None
    thumbnail_url: str | None
    tags: list[str]
    merge_count: int
    pr_count: int
    created_at: datetime

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        return format_utc(value)


class PullRequestNestedSummary(BaseModel):
    id: int
    title: str | None


class RepositoryNestedSummary(BaseModel):
    id: int
    title: str


class ContributionSummary(BaseModel):
    merge_id: int
    pull_request: PullRequestNestedSummary
    repository: RepositoryNestedSummary
    final_grade: ContributionGrade
    credit_text: str
    citation_url: str
    merged_at: datetime

    @field_serializer("merged_at")
    def serialize_merged_at(self, value: datetime) -> str:
        return format_utc(value)


class PullRequestSummary(BaseModel):
    id: int
    repository: RepositoryNestedSummary
    title: str | None
    status: PullRequestStatus
    visibility: Visibility
    ai_grade: ContributionGrade | None
    author_grade_override: ContributionGrade | None
    first_drafted_at: datetime
    last_saved_at: datetime
    submitted_at: datetime | None

    @field_serializer("first_drafted_at", "last_saved_at", "submitted_at")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        if value is None:
            return None
        return format_utc(value)


class ContributorStatsResponse(BaseModel):
    total_prs: int
    merged_prs: int
    major_count: int
    normal_count: int
    minor_count: int
    merge_ratio: float
    last_activity_at: datetime | None

    @field_serializer("last_activity_at")
    def serialize_last_activity_at(self, value: datetime | None) -> str | None:
        if value is None:
            return None
        return format_utc(value)


class AuthorStatsResponse(BaseModel):
    repository_count: int
    received_prs: int
    merged_prs: int
    merge_ratio: float
    avg_review_days: float
    last_activity_at: datetime | None

    @field_serializer("last_activity_at")
    def serialize_last_activity_at(self, value: datetime | None) -> str | None:
        if value is None:
            return None
        return format_utc(value)


class BadgesResponse(BaseModel):
    badges: list[dict] = Field(default_factory=list)
