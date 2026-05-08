from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, field_serializer

from app.schemas.auth import format_utc


class NotificationType(StrEnum):
    PR_SUBMITTED = "PR_SUBMITTED"
    PR_RESUBMITTED = "PR_RESUBMITTED"
    PR_COMMENT_ADDED = "PR_COMMENT_ADDED"
    PR_ACCEPTED = "PR_ACCEPTED"
    PR_CHANGES_REQUESTED = "PR_CHANGES_REQUESTED"
    PR_REJECTED = "PR_REJECTED"
    PR_MERGED = "PR_MERGED"
    GRADE_ADJUSTED = "GRADE_ADJUSTED"


class NotificationItem(BaseModel):
    id: int
    type: NotificationType
    payload: dict
    is_read: bool
    created_at: datetime
    read_at: datetime | None

    @field_serializer("created_at", "read_at")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        if value is None:
            return None
        return format_utc(value)


class NotificationListResponse(BaseModel):
    items: list[NotificationItem]
    total: int
    unread_count: int
    page: int
    size: int


class UnreadCountResponse(BaseModel):
    count: int


class NotificationReadResponse(BaseModel):
    id: int
    is_read: bool
    read_at: datetime

    @field_serializer("read_at")
    def serialize_read_at(self, value: datetime) -> str:
        return format_utc(value)


class NotificationReadAllResponse(BaseModel):
    updated_count: int
