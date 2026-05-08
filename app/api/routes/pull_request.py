from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.pull_request import (
    AiAnalysisResponse,
    ConflictCheckItem,
    ContributorCommentRequest,
    ContributorCommentResponse,
    CreateDraftResponse,
    DraftResponse,
    LatestAiAnalysisSummary,
    RepositoryInfo,
    SaveDraftRequest,
    SaveDraftResponse,
    SubmitPRRequest,
    SubmitPRResponse,
)
from app.services import pull_request as pr_service

router = APIRouter(tags=["pull-requests"])


@router.post(
    "/repositories/{repo_id}/pull-requests/draft",
    response_model=CreateDraftResponse,
)
def create_or_get_draft(
    repo_id: int,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CreateDraftResponse:
    pr, created = pr_service.create_or_get_draft(db, repo_id=repo_id, user_id=current_user.id)
    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return CreateDraftResponse(
        pull_request_id=pr.id,
        first_drafted_at=pr.first_drafted_at,
        last_saved_at=pr.last_saved_at,
        save_count=pr.save_count,
        raw_content=pr.raw_content,
    )


@router.get("/pull-requests/{pr_id}/draft", response_model=DraftResponse)
def get_draft(
    pr_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DraftResponse:
    pr = pr_service.get_draft(db, pr_id=pr_id, user_id=current_user.id)
    latest = None
    if pr.analyses:
        top = max(pr.analyses, key=lambda a: a.run_seq)
        latest = LatestAiAnalysisSummary(
            ai_grade=top.ai_grade,
            score_total=top.score_total,
            run_seq=top.run_seq,
        )
    return DraftResponse(
        pull_request_id=pr.id,
        repository=RepositoryInfo(id=pr.repository.id, title=pr.repository.title),
        first_drafted_at=pr.first_drafted_at,
        last_saved_at=pr.last_saved_at,
        save_count=pr.save_count,
        raw_content=pr.raw_content,
        latest_ai_analysis=latest,
    )


@router.patch("/pull-requests/{pr_id}/draft", response_model=SaveDraftResponse)
def save_draft(
    pr_id: int,
    payload: SaveDraftRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SaveDraftResponse:
    pr = pr_service.save_draft(db, pr_id=pr_id, user_id=current_user.id, raw_content=payload.raw_content)
    return SaveDraftResponse(
        pull_request_id=pr.id,
        last_saved_at=pr.last_saved_at,
        save_count=pr.save_count,
    )


@router.post("/pull-requests/{pr_id}/ai-analyze", response_model=AiAnalysisResponse)
def analyze_pr(
    pr_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AiAnalysisResponse:
    analysis = pr_service.analyze_pr(db, pr_id=pr_id, user_id=current_user.id)
    return _to_analysis_response(analysis)


@router.get("/pull-requests/{pr_id}/ai-analysis", response_model=AiAnalysisResponse)
def get_ai_analysis(
    pr_id: int,
    run_seq: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AiAnalysisResponse:
    analysis = pr_service.get_ai_analysis(db, pr_id=pr_id, user_id=current_user.id, run_seq=run_seq)
    return _to_analysis_response(analysis)


@router.post("/pull-requests/{pr_id}/submit", response_model=SubmitPRResponse)
def submit_pr(
    pr_id: int,
    payload: SubmitPRRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SubmitPRResponse:
    pr = pr_service.submit_pr(db, pr_id=pr_id, user_id=current_user.id, visibility=payload.visibility)
    return SubmitPRResponse(
        pull_request_id=pr.id,
        status=pr.status,
        visibility=pr.visibility,
        submitted_at=pr.submitted_at,
    )


@router.patch("/pull-requests/{pr_id}/contributor-comment", response_model=ContributorCommentResponse)
def save_contributor_comment(
    pr_id: int,
    payload: ContributorCommentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ContributorCommentResponse:
    pr = pr_service.save_contributor_comment(
        db,
        pr_id=pr_id,
        user_id=current_user.id,
        comment=payload.contributor_comment,
    )
    return ContributorCommentResponse(
        pull_request_id=pr.id,
        contributor_comment=pr.contributor_comment,
    )


def _to_analysis_response(analysis) -> AiAnalysisResponse:
    return AiAnalysisResponse(
        id=analysis.id,
        pull_request_id=analysis.pull_request_id,
        run_seq=analysis.run_seq,
        generated_title=analysis.generated_title or "",
        summary=analysis.summary or "",
        structured_content=analysis.structured_content or {},
        contribution_types=analysis.contribution_types or [],
        score_scope=analysis.score_scope,
        score_permanence=analysis.score_permanence,
        score_cascade=analysis.score_cascade,
        score_alignment=analysis.score_alignment,
        score_specificity=analysis.score_specificity,
        score_total=analysis.score_total,
        ai_grade=analysis.ai_grade,
        rationale=analysis.rationale or "",
        missing_info=analysis.missing_info or [],
        conflict_checks=[
            ConflictCheckItem(
                risk_level=cc.risk_level,
                check_target=cc.check_target,
                passed=cc.passed,
                detail=cc.detail or "",
            )
            for cc in analysis.conflict_checks
        ],
        model_name=analysis.model_name or "",
        created_at=analysis.created_at,
    )
