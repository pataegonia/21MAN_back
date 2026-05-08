from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CreateDraftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pull_request_id: int
    first_drafted_at: datetime
    last_saved_at: datetime
    save_count: int
    raw_content: str | None


class RepositoryInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str


class LatestAiAnalysisSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ai_grade: str
    score_total: int
    run_seq: int


class DraftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pull_request_id: int
    repository: RepositoryInfo
    first_drafted_at: datetime
    last_saved_at: datetime
    save_count: int
    raw_content: str | None
    latest_ai_analysis: LatestAiAnalysisSummary | None


class SaveDraftRequest(BaseModel):
    raw_content: str


class SaveDraftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pull_request_id: int
    last_saved_at: datetime
    save_count: int


class ConflictCheckItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    risk_level: str
    check_target: str
    passed: bool
    detail: str


class AiAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pull_request_id: int
    run_seq: int
    generated_title: str
    summary: str
    structured_content: dict
    contribution_types: list[str]
    score_scope: int
    score_permanence: int
    score_cascade: int
    score_alignment: int
    score_specificity: int
    score_total: int
    ai_grade: str
    rationale: str
    missing_info: list[str]
    conflict_checks: list[ConflictCheckItem]
    model_name: str
    created_at: datetime


class SubmitPRRequest(BaseModel):
    visibility: str


class SubmitPRResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pull_request_id: int
    status: str
    visibility: str
    submitted_at: datetime


class ContributorCommentRequest(BaseModel):
    contributor_comment: str


class ContributorCommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pull_request_id: int
    contributor_comment: str


# ---------------------------------------------------------------------------
# PR 조회 (05-pull-requests-query)
# ---------------------------------------------------------------------------

class PRDetailRepositoryAuthor(BaseModel):
    username: str


class PRDetailRepository(BaseModel):
    id: int
    title: str
    author: PRDetailRepositoryAuthor


class PRDetailAuthor(BaseModel):
    id: int
    username: str
    avatar: str | None


class RejectReasonInfo(BaseModel):
    id: int
    category: str
    detail: str
    created_at: datetime


class MergeInfo(BaseModel):
    id: int
    final_grade: str
    credit_text: str
    author_comment: str | None
    citation_url: str
    merged_at: datetime


class ViewLogSummary(BaseModel):
    total_views: int
    first_viewed_at: datetime | None


class PRDetailResponse(BaseModel):
    id: int
    repository: PRDetailRepository
    author: PRDetailAuthor
    title: str | None
    raw_content: str | None
    contribution_types: list[str]
    visibility: str
    status: str
    contributor_comment: str | None
    author_grade_override: str | None
    author_grade_override_reason: str | None
    author_review_comment: str | None
    changes_requested_reason: str | None
    reject_reason: RejectReasonInfo | None
    merge_info: MergeInfo | None
    view_log_summary: ViewLogSummary | None
    first_drafted_at: datetime
    submitted_at: datetime | None
    reviewed_at: datetime | None
    merged_at: datetime | None
    created_at: datetime
    updated_at: datetime


class PRListAuthor(BaseModel):
    username: str
    avatar: str | None


class PRListItem(BaseModel):
    id: int
    repository: RepositoryInfo
    author: PRListAuthor
    title: str | None
    status: str
    visibility: str
    contribution_types: list[str]
    ai_grade: str | None
    submitted_at: datetime | None


class PRListResponse(BaseModel):
    items: list[PRListItem]
    total: int
    page: int
    size: int
