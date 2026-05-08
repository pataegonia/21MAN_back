from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.core.security import AccessTokenExpiredError, AccessTokenInvalidError, decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.auth import get_user_by_id

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AppError("UNAUTHORIZED", "Authentication is required", status_code=401)

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except AccessTokenExpiredError as exc:
        raise AppError("UNAUTHORIZED", "Authentication is required", status_code=401) from exc
    except (AccessTokenInvalidError, KeyError, TypeError, ValueError) as exc:
        raise AppError("UNAUTHORIZED", "Authentication is required", status_code=401) from exc

    user = get_user_by_id(db, user_id)
    if user is None:
        raise AppError("UNAUTHORIZED", "Authentication is required", status_code=401)
    return user


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    if credentials is None:
        return None
    try:
        return get_current_user(credentials=credentials, db=db)
    except AppError:
        return None
