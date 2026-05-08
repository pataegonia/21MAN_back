from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import AccessTokenResponse, LoginRequest, LogoutRequest, RefreshRequest, RegisterRequest, RegisterResponse, TokenPairResponse, UserResponse
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)) -> User:
    return auth_service.register_user(
        db,
        email=str(payload.email),
        password=payload.password,
        username=payload.username,
        user_agent=request.headers.get("user-agent"),
        ip=_client_ip(request),
    )


@router.post("/login", response_model=TokenPairResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> TokenPairResponse:
    return auth_service.login_user(
        db,
        email=str(payload.email),
        password=payload.password,
        user_agent=request.headers.get("user-agent"),
        ip=_client_ip(request),
    )


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(payload: RefreshRequest, request: Request, db: Session = Depends(get_db)) -> AccessTokenResponse:
    return auth_service.refresh_tokens(
        db,
        raw_refresh_token=payload.refresh_token,
        user_agent=request.headers.get("user-agent"),
        ip=_client_ip(request),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    payload: LogoutRequest,
    _: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    auth_service.logout_user(db, user_id=current_user.id, raw_refresh_token=payload.refresh_token)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


def _client_ip(request: Request) -> str | None:
    if request.client is None:
        return None
    return request.client.host
