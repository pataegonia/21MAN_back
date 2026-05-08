from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.notifications import (
    NotificationListResponse,
    NotificationReadAllResponse,
    NotificationReadResponse,
    NotificationType,
    UnreadCountResponse,
)
from app.services import notifications as notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationListResponse)
def list_notifications(
    unread_only: bool = False,
    notification_type: Annotated[list[NotificationType] | None, Query(alias="type")] = None,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationListResponse:
    return notification_service.list_notifications(
        db,
        user=current_user,
        unread_only=unread_only,
        types=notification_type,
        page=page,
        size=size,
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
def unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UnreadCountResponse:
    return notification_service.count_unread(db, user=current_user)


@router.post("/{notification_id}/read", response_model=NotificationReadResponse)
def read_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationReadResponse:
    return notification_service.mark_read(db, user=current_user, notification_id=notification_id)


@router.post("/read-all", response_model=NotificationReadAllResponse)
def read_all_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationReadAllResponse:
    return notification_service.mark_all_read(db, user=current_user)
