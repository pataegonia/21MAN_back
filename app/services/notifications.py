from datetime import UTC, datetime

from sqlalchemy import desc, func, select, update
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import AppError
from app.models.notification import Notification
from app.models.pull_request import PullRequest
from app.models.repository import Repository
from app.models.user import User
from app.schemas.notifications import (
    NotificationItem,
    NotificationListResponse,
    NotificationReadAllResponse,
    NotificationReadResponse,
    NotificationType,
    UnreadCountResponse,
)

MAX_PAGE_SIZE = 100
AUTHOR_ACTION_TYPES = {
    NotificationType.PR_ACCEPTED,
    NotificationType.PR_CHANGES_REQUESTED,
    NotificationType.PR_REJECTED,
    NotificationType.PR_MERGED,
    NotificationType.GRADE_ADJUSTED,
}
CONTRIBUTOR_ACTION_TYPES = {
    NotificationType.PR_SUBMITTED,
    NotificationType.PR_RESUBMITTED,
    NotificationType.PR_COMMENT_ADDED,
}


def list_notifications(
    db: Session,
    *,
    user: User,
    unread_only: bool,
    types: list[NotificationType] | None,
    page: int,
    size: int,
) -> NotificationListResponse:
    page, size = _normalize_pagination(page, size)
    statement = select(Notification).where(Notification.recipient_id == user.id)
    if unread_only:
        statement = statement.where(Notification.is_read.is_(False))
    if types:
        statement = statement.where(Notification.type.in_([item.value for item in types]))
    statement = statement.order_by(desc(Notification.created_at), desc(Notification.id))

    total = db.scalar(select(func.count()).select_from(statement.order_by(None).subquery())) or 0
    unread_count = count_unread(db, user=user).count
    notifications = list(db.scalars(statement.offset((page - 1) * size).limit(size)))

    return NotificationListResponse(
        items=[_to_item(db, notification) for notification in notifications],
        total=total,
        unread_count=unread_count,
        page=page,
        size=size,
    )


def count_unread(db: Session, *, user: User) -> UnreadCountResponse:
    count = db.scalar(
        select(func.count(Notification.id)).where(
            Notification.recipient_id == user.id,
            Notification.is_read.is_(False),
        )
    ) or 0
    return UnreadCountResponse(count=count)


def mark_read(db: Session, *, user: User, notification_id: int) -> NotificationReadResponse:
    notification = db.get(Notification, notification_id)
    if notification is None or notification.recipient_id != user.id:
        raise AppError("NOTIFICATION_NOT_FOUND", "Notification not found", status_code=404)

    if not notification.is_read:
        notification.is_read = True
        notification.read_at = _now()
        db.commit()
        db.refresh(notification)

    return NotificationReadResponse(
        id=notification.id,
        is_read=notification.is_read,
        read_at=notification.read_at or _now(),
    )


def mark_all_read(db: Session, *, user: User) -> NotificationReadAllResponse:
    now = _now()
    unread_ids = list(
        db.scalars(
            select(Notification.id).where(
                Notification.recipient_id == user.id,
                Notification.is_read.is_(False),
            )
        )
    )
    if unread_ids:
        db.execute(
            update(Notification)
            .where(Notification.id.in_(unread_ids))
            .values(is_read=True, read_at=now)
        )
        db.commit()
    return NotificationReadAllResponse(updated_count=len(unread_ids))


def _to_item(db: Session, notification: Notification) -> NotificationItem:
    return NotificationItem(
        id=notification.id,
        type=NotificationType(notification.type),
        payload=_normalized_payload(db, notification),
        is_read=notification.is_read,
        created_at=notification.created_at,
        read_at=notification.read_at,
    )


def _normalized_payload(db: Session, notification: Notification) -> dict:
    payload = dict(notification.payload or {})
    pr_id = payload.get("pr_id") or payload.get("pull_request_id")
    if pr_id:
        payload["pr_id"] = pr_id
        payload.pop("pull_request_id", None)
        pr = db.scalar(
            select(PullRequest)
            .where(PullRequest.id == pr_id)
            .options(
                selectinload(PullRequest.repository).selectinload(Repository.author),
                selectinload(PullRequest.author),
                selectinload(PullRequest.merge),
            )
        )
        if pr is not None:
            payload.setdefault("pr_title", pr.title)
            payload.setdefault("repo_id", pr.repository_id)
            payload.setdefault("repo_title", pr.repository.title)
            actor = _infer_actor(notification, pr, payload)
            if actor is not None:
                payload.setdefault("actor_id", actor.id)
                payload.setdefault("actor_username", actor.username)
                payload.setdefault("actor_avatar_url", actor.avatar_url)
            if notification.type == NotificationType.PR_MERGED and pr.merge is not None:
                payload.setdefault("merge_id", pr.merge.id)
                payload.setdefault("citation_url", pr.merge.citation_url)
                payload.setdefault("final_grade", pr.merge.final_grade)
    return payload


def _infer_actor(notification: Notification, pr: PullRequest, payload: dict) -> User | None:
    actor_id = payload.get("actor_id") or payload.get("contributor_id")
    if actor_id == pr.author_id:
        return pr.author
    if actor_id == pr.repository.author_id:
        return pr.repository.author

    notification_type = NotificationType(notification.type)
    if notification_type in CONTRIBUTOR_ACTION_TYPES:
        return pr.author
    if notification_type in AUTHOR_ACTION_TYPES:
        return pr.repository.author
    return None


def _normalize_pagination(page: int, size: int) -> tuple[int, int]:
    if page < 1:
        raise AppError("INVALID_PAGINATION", "Page must be greater than or equal to 1", status_code=400)
    if size < 1 or size > MAX_PAGE_SIZE:
        raise AppError("INVALID_PAGINATION", f"Size must be between 1 and {MAX_PAGE_SIZE}", status_code=400)
    return page, size


def _now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)
