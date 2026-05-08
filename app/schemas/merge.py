from datetime import datetime

from pydantic import BaseModel


class MergePRInfo(BaseModel):
    id: int
    title: str | None
    summary: str | None
    contribution_types: list[str]
    first_drafted_at: datetime
    submitted_at: datetime | None


class MergeRepositoryInfo(BaseModel):
    id: int
    title: str
    thumbnail: str | None


class MergeUserInfo(BaseModel):
    username: str
    avatar: str | None


class MergeDetailResponse(BaseModel):
    id: int
    pull_request: MergePRInfo
    repository: MergeRepositoryInfo
    contributor: MergeUserInfo
    author: MergeUserInfo
    final_grade: str
    credit_text: str
    author_comment: str | None
    citation_url: str
    merged_at: datetime
