from datetime import datetime
from enum import StrEnum
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_serializer, field_validator, model_validator

from app.models.enums import ContributionGrade, PullRequestStatus, Visibility
from app.schemas.auth import format_utc

T = TypeVar("T")


class RecruitingAreaSlug(StrEnum):
    CHARACTER_ADD = "character_add"
    CHARACTER_EDIT = "character_edit"
    WORLDBUILDING = "worldbuilding"
    REGION = "region"
    EVENT_EPISODE = "event_episode"
    ITEM_ABILITY_RULE = "item_ability_rule"
    RELATIONSHIP = "relationship"
    DIALOGUE_TONE = "dialogue_tone"
    OTHER = "other"


class PageResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int


class ExternalLink(BaseModel):
    label: str = Field(min_length=1, max_length=50)
    url: HttpUrl


class ReadmeNamedItem(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=5000)


class ReadmePayload(BaseModel):
    overview: str | None = Field(default=None, max_length=5000)
    characters: list[ReadmeNamedItem] | None = Field(default=None, max_length=50)
    regions: list[ReadmeNamedItem] | None = Field(default=None, max_length=50)
    world_rules: list[str] | None = Field(default=None, max_length=50)
    forbidden_settings: list[str] | None = Field(default=None, max_length=50)

    @field_validator("world_rules", "forbidden_settings")
    @classmethod
    def validate_text_items(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return value
        normalized = [item.strip() for item in value if item.strip()]
        if len(normalized) != len(value):
            raise ValueError("Items must not be blank")
        if any(len(item) > 5000 for item in normalized):
            raise ValueError("Each item must be 5000 characters or fewer")
        return normalized


class RepositoryCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    thumbnail_url: str | None = Field(default=None, max_length=500)
    tags: list[str] = Field(default_factory=list, max_length=10)
    external_links: list[ExternalLink] = Field(default_factory=list, max_length=5)
    readme: ReadmePayload | None = None
    recruiting_areas: list[RecruitingAreaSlug] = Field(default_factory=list, max_length=9)
    contribution_guidelines: str | None = Field(default=None, max_length=5000)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: list[str]) -> list[str]:
        return normalize_tags(value)

    @field_validator("recruiting_areas")
    @classmethod
    def validate_recruiting_areas(cls, value: list[RecruitingAreaSlug]) -> list[RecruitingAreaSlug]:
        return dedupe_recruiting_areas(value)


class RepositoryUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    thumbnail_url: str | None = Field(default=None, max_length=500)
    tags: list[str] | None = Field(default=None, max_length=10)
    external_links: list[ExternalLink] | None = Field(default=None, max_length=5)
    readme: ReadmePayload | None = None
    recruiting_areas: list[RecruitingAreaSlug] | None = Field(default=None, max_length=9)
    contribution_guidelines: str | None = Field(default=None, max_length=5000)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return value
        return normalize_tags(value)

    @field_validator("recruiting_areas")
    @classmethod
    def validate_recruiting_areas(cls, value: list[RecruitingAreaSlug] | None) -> list[RecruitingAreaSlug] | None:
        if value is None:
            return value
        return dedupe_recruiting_areas(value)

    @model_validator(mode="before")
    @classmethod
    def reject_invalid_nulls(cls, data):
        if not isinstance(data, dict):
            return data
        non_nullable_fields = {"title", "tags", "external_links", "readme", "recruiting_areas"}
        null_fields = sorted(field for field in non_nullable_fields if field in data and data[field] is None)
        if null_fields:
            joined = ", ".join(null_fields)
            raise ValueError(f"{joined} cannot be null")
        return data


class UserSummary(BaseModel):
    id: int
    username: str
    avatar_url: str | None


class ReadmeResponse(BaseModel):
    overview: str | None
    characters: list[ReadmeNamedItem]
    regions: list[ReadmeNamedItem]
    world_rules: list[str]
    forbidden_settings: list[str]


class RepositoryDetailResponse(BaseModel):
    id: int
    title: str
    description: str | None
    thumbnail_url: str | None
    tags: list[str]
    external_links: list[ExternalLink]
    readme: ReadmeResponse
    recruiting_areas: list[RecruitingAreaSlug]
    contribution_guidelines: str | None
    author: UserSummary
    pr_count: int
    merge_count: int
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        return format_utc(value)


class RepositoryListItem(BaseModel):
    id: int
    title: str
    description: str | None
    thumbnail_url: str | None
    tags: list[str]
    author: UserSummary
    recruiting_areas: list[RecruitingAreaSlug]
    pr_count: int
    merge_count: int
    created_at: datetime

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        return format_utc(value)


class ContributorSummary(BaseModel):
    user: UserSummary
    merge_count: int
    major_count: int
    normal_count: int
    minor_count: int
    last_merged_at: datetime | None

    @field_serializer("last_merged_at")
    def serialize_last_merged_at(self, value: datetime | None) -> str | None:
        if value is None:
            return None
        return format_utc(value)


class MergeSummary(BaseModel):
    id: int
    pull_request_id: int
    contributor: UserSummary
    final_grade: ContributionGrade
    credit_text: str
    citation_url: str
    merged_at: datetime

    @field_serializer("merged_at")
    def serialize_merged_at(self, value: datetime) -> str:
        return format_utc(value)


class RepositoryNestedSummary(BaseModel):
    id: int
    title: str


class PullRequestListItem(BaseModel):
    id: int
    repository: RepositoryNestedSummary
    author: UserSummary
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


class RepositoryStatsResponse(BaseModel):
    repository_id: int
    received_prs: int
    merged_prs: int
    merge_ratio: float
    awaiting_review_prs: int
    awaiting_merge_prs: int
    awaiting_resubmit_prs: int
    rejected_prs: int


def normalize_tags(value: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for tag in value:
        cleaned = tag.strip()
        lowered = cleaned.lower()
        if not cleaned:
            raise ValueError("Tag must not be blank")
        if len(cleaned) > 20:
            raise ValueError("Tag must be 20 characters or fewer")
        if lowered not in seen:
            seen.add(lowered)
            normalized.append(cleaned)
    return normalized


def dedupe_recruiting_areas(value: list[RecruitingAreaSlug]) -> list[RecruitingAreaSlug]:
    normalized: list[RecruitingAreaSlug] = []
    seen: set[RecruitingAreaSlug] = set()
    for item in value:
        if item not in seen:
            seen.add(item)
            normalized.append(item)
    return normalized
