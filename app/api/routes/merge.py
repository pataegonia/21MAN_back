from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.db.session import get_db
from app.models.user import User
from app.repositories import merge as merge_repo
from app.schemas.merge import MergeDetailResponse, MergePRInfo, MergeRepositoryInfo, MergeUserInfo

router = APIRouter(tags=["merges"])


@router.get("/merges/{merge_id}", response_model=MergeDetailResponse)
def get_merge(
    merge_id: int,
    db: Session = Depends(get_db),
) -> MergeDetailResponse:
    m = merge_repo.get_merge_for_detail(db, merge_id)
    if m is None:
        raise AppError("MERGE_NOT_FOUND", "존재하지 않는 기여 기록입니다.", status_code=404)

    pr = m.pull_request
    latest = max(pr.analyses, key=lambda a: a.run_seq) if pr.analyses else None
    contributor = db.get(User, m.contributor_id)
    author = db.get(User, m.author_id)

    return MergeDetailResponse(
        id=m.id,
        pull_request=MergePRInfo(
            id=pr.id,
            title=latest.generated_title if latest else None,
            summary=latest.summary if latest else None,
            contribution_types=latest.contribution_types or [] if latest else [],
            first_drafted_at=pr.first_drafted_at,
            submitted_at=pr.submitted_at,
        ),
        repository=MergeRepositoryInfo(
            id=pr.repository.id,
            title=pr.repository.title,
            thumbnail=pr.repository.thumbnail_url,
        ),
        contributor=MergeUserInfo(username=contributor.username, avatar=contributor.avatar_url),
        author=MergeUserInfo(username=author.username, avatar=author.avatar_url),
        final_grade=m.final_grade,
        credit_text=m.credit_text,
        author_comment=m.author_comment,
        citation_url=m.citation_url,
        merged_at=m.merged_at,
    )
