import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_serializer, field_validator

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]+$")


def format_utc(value: datetime) -> str:
    return value.isoformat().removesuffix("+00:00") + "Z"


class RegisterRequest(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=72)
    username: str = Field(min_length=3, max_length=30)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be 72 bytes or fewer")
        return value

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if not USERNAME_PATTERN.fullmatch(value):
            raise ValueError("Username can contain only letters, numbers, and underscores")
        return value


class LoginRequest(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=1, max_length=72)

    @field_validator("password")
    @classmethod
    def validate_password_bytes(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be 72 bytes or fewer")
        return value


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=20, max_length=200)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(min_length=20, max_length=200)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    username: str
    avatar_url: str | None
    bio: str | None
    created_at: datetime | None = None

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime | None) -> str | None:
        if value is None:
            return None
        return format_utc(value)


class RegisterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    username: str
    created_at: datetime

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        return format_utc(value)


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
