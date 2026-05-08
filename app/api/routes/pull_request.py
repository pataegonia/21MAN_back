import hashlib

from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_user_optional
from app.db.session import get_db
from app.models.user import User
from app.repositories import pull_request as pr_repo
from app.schemas.pull_request import (
    AiAnalysisResponse,
    ConflictCheckItem,
    ContributorCommentRequest,
    ContributorCommentResponse,
    CreateDraftResponse,
    DraftResponse,
    LatestAiAnalysisSummary,
    MergeInfo,
    PRDetailAuthor,
    PRDetailRepository,
    PRDetailRepositoryAuthor,
    PRDetailResponse,
    PRListAuthor,
    PRListItem,
    PRListResponse,
    RejectReasonInfo,
    RepositoryInfo,
    SaveDraftRequest,
    SaveDraftResponse,
    SubmitPRRequest,
    SubmitPRResponse,
    ViewLogSummary,
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


@router.get("/pull-requests/{pr_id}", response_model=PRDetailResponse)
def get_pr_detail(
    pr_id: int,
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
) -> PRDetailResponse:
    client_ip = (request.client.host if request.client else None) or "unknown"
    ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()
    current_user_id = current_user.id if current_user else None

    pr, is_owner = pr_service.get_pr_detail(
        db, pr_id=pr_id, current_user_id=current_user_id, ip_hash=ip_hash
    )

    latest = max(pr.analyses, key=lambda a: a.run_seq) if pr.analyses else None
    active_reject = pr_repo.get_active_reject_reason(pr)

    view_log_summary = None
    if is_owner and pr.view_logs:
        view_log_summary = ViewLogSummary(
            total_views=len(pr.view_logs),
            first_viewed_at=min(vl.viewed_at for vl in pr.view_logs),
        )

    reject_reason_info = None
    if active_reject:
        reject_reason_info = RejectReasonInfo(
            id=active_reject.id,
            category=active_reject.category,
            detail=active_reject.detail,
            created_at=active_reject.created_at,
        )

    merge_info = None
    if pr.merge:
        m = pr.merge
        merge_info = MergeInfo(
            id=m.id,
            final_grade=m.final_grade,
            credit_text=m.credit_text,
            author_comment=m.author_comment,
            citation_url=m.citation_url,
            merged_at=m.merged_at,
        )

    return PRDetailResponse(
        id=pr.id,
        repository=PRDetailRepository(
            id=pr.repository.id,
            title=pr.repository.title,
            author=PRDetailRepositoryAuthor(username=pr.repository.author.username),
        ),
        author=PRDetailAuthor(
            id=pr.author.id,
            username=pr.author.username,
            avatar=pr.author.avatar_url,
        ),
        title=latest.generated_title if latest else None,
        raw_content=pr.raw_content,
        contribution_types=latest.contribution_types or [] if latest else [],
        visibility=pr.visibility,
        status=pr.status,
        contributor_comment=pr.contributor_comment,
        author_grade_override=pr.author_grade_override,
        author_grade_override_reason=pr.author_grade_override_reason,
        author_review_comment=pr.author_review_comment,
        changes_requested_reason=pr.changes_requested_reason,
        reject_reason=reject_reason_info,
        merge_info=merge_info,
        view_log_summary=view_log_summary,
        first_drafted_at=pr.first_drafted_at,
        submitted_at=pr.submitted_at,
        reviewed_at=pr.reviewed_at,
        merged_at=pr.merged_at,
        created_at=pr.created_at,
        updated_at=pr.updated_at,
    )


@router.get("/pull-requests", response_model=PRListResponse)
def list_prs(
    repo_id: int | None = None,
    author: str | None = None,
    status: list[str] = Query(default=[]),
    type: str | None = None,
    grade: str | None = None,
    page: int = 1,
    size: int = 20,
    current_user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
) -> PRListResponse:
    current_user_id = current_user.id if current_user else None
    rows, total = pr_service.list_prs(
        db,
        repo_id=repo_id,
        author_username=author,
        statuses=status,
        contribution_type=type,
        grade=grade,
        current_user_id=current_user_id,
        page=page,
        size=size,
    )
    items = [
        PRListItem(
            id=pr.id,
            repository=RepositoryInfo(id=pr.repository.id, title=pr.repository.title),
            author=PRListAuthor(username=pr.author.username, avatar=pr.author.avatar_url),
            title=analysis.generated_title if analysis else None,
            status=pr.status,
            visibility=pr.visibility,
            contribution_types=analysis.contribution_types or [] if analysis else [],
            ai_grade=analysis.ai_grade if analysis else None,
            submitted_at=pr.submitted_at,
        )
        for pr, analysis in rows
    ]
    return PRListResponse(items=items, total=total, page=page, size=size)


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
