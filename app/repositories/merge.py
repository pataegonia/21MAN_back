from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, subqueryload

from app.models.merge import Merge
from app.models.pull_request import PullRequest


def get_merge_for_detail(db: Session, merge_id: int) -> Merge | None:
    stmt = (
        select(Merge)
        .options(
            joinedload(Merge.pull_request).joinedload(PullRequest.repository),
            joinedload(Merge.pull_request).subqueryload(PullRequest.analyses),
        )
        .where(Merge.id == merge_id)
    )
    return db.scalar(stmt)
