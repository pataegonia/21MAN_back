from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AppError
from app.core.security import create_access_token, generate_opaque_token, hash_ip, hash_password, hash_token, verify_password
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories import auth as auth_repo
from app.schemas.auth import AuthResponse, RefreshResponse


def _now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def register_user(
    db: Session,
    *,
    email: str,
    password: str,
    username: str,
    user_agent: str | None,
    ip: str | None,
) -> AuthResponse:
    normalized_email = email.lower()

    if auth_repo.get_user_by_email(db, normalized_email):
        raise AppError("EMAIL_TAKEN", "Email is already registered", status_code=409)
    if auth_repo.get_user_by_username(db, username):
        raise AppError("USERNAME_TAKEN", "Username is already taken", status_code=409)

    user = User(
        email=normalized_email,
        username=username,
        password_hash=hash_password(password),
    )
    db.add(user)
    db.flush()

    refresh_token = _issue_refresh_token(db, user_id=user.id, user_agent=user_agent, ip=ip)
    db.commit()
    db.refresh(user)

    return _auth_response(user, refresh_token)


def login_user(
    db: Session,
    *,
    email: str,
    password: str,
    user_agent: str | None,
    ip: str | None,
) -> AuthResponse:
    user = auth_repo.get_user_by_email(db, email.lower())
    if user is None or not verify_password(password, user.password_hash):
        raise AppError("INVALID_CREDENTIALS", "Invalid email or password", status_code=401)

    refresh_token = _issue_refresh_token(db, user_id=user.id, user_agent=user_agent, ip=ip)
    db.commit()

    return _auth_response(user, refresh_token)


def refresh_tokens(
    db: Session,
    *,
    raw_refresh_token: str,
    user_agent: str | None,
    ip: str | None,
) -> RefreshResponse:
    now = _now()
    token_row = auth_repo.get_refresh_token_by_hash(db, hash_token(raw_refresh_token))

    if token_row is None:
        raise AppError("INVALID_TOKEN", "Invalid refresh token", status_code=401)
    if token_row.expires_at < now:
        raise AppError("EXPIRED_TOKEN", "Refresh token has expired", status_code=401)
    if token_row.revoked_at is not None:
        _revoke_family(db, token_row.family_id, reason="reuse_detected", now=now)
        db.commit()
        raise AppError("TOKEN_REUSED", "Refresh token was already used", status_code=401)

    token_row.revoked_at = now
    token_row.revoke_reason = "rotated"
    new_refresh_token = _issue_refresh_token(
        db,
        user_id=token_row.user_id,
        user_agent=user_agent,
        ip=ip,
        family_id=token_row.family_id,
        parent_id=token_row.id,
        now=now,
    )
    db.commit()

    return RefreshResponse(
        access_token=create_access_token(str(token_row.user_id)),
        refresh_token=new_refresh_token,
        access_expires_in=settings.access_token_expires_in,
        refresh_expires_in=settings.refresh_token_expires_in,
    )


def logout_user(db: Session, *, user_id: int, raw_refresh_token: str) -> None:
    token_row = auth_repo.get_refresh_token_by_hash(db, hash_token(raw_refresh_token))
    if token_row is not None and token_row.user_id == user_id:
        _revoke_family(db, token_row.family_id, reason="logout", now=_now())
        db.commit()


def _issue_refresh_token(
    db: Session,
    *,
    user_id: int,
    user_agent: str | None,
    ip: str | None,
    family_id: str | None = None,
    parent_id: int | None = None,
    now: datetime | None = None,
) -> str:
    issued_at = now or _now()
    raw_token = generate_opaque_token()
    db.add(
        RefreshToken(
            user_id=user_id,
            token_hash=hash_token(raw_token),
            family_id=family_id or str(uuid4()),
            parent_id=parent_id,
            issued_at=issued_at,
            expires_at=issued_at + timedelta(days=settings.refresh_token_expire_days),
            user_agent=user_agent,
            ip_hash=hash_ip(ip),
        )
    )
    return raw_token


def _revoke_family(db: Session, family_id: str, *, reason: str, now: datetime) -> None:
    for token in auth_repo.list_refresh_tokens_by_family(db, family_id):
        if token.revoked_at is None:
            token.revoked_at = now
            token.revoke_reason = reason if reason != "reuse_detected" else "family_revoked"


def _auth_response(user: User, refresh_token: str) -> AuthResponse:
    return AuthResponse(
        user=user,
        access_token=create_access_token(str(user.id)),
        refresh_token=refresh_token,
        access_expires_in=settings.access_token_expires_in,
        refresh_expires_in=settings.refresh_token_expires_in,
    )
