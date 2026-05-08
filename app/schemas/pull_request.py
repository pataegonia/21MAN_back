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
