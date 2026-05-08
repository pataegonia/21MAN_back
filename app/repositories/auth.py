from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken
from app.models.user import User


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    statement = select(User).where(func.lower(User.email) == email.lower())
    return db.scalar(statement)


def get_user_by_username(db: Session, username: str) -> User | None:
    statement = select(User).where(func.lower(User.username) == username.lower())
    return db.scalar(statement)


def get_refresh_token_by_hash(db: Session, token_hash: str) -> RefreshToken | None:
    statement = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    return db.scalar(statement)


def list_refresh_tokens_by_family(db: Session, family_id: str) -> list[RefreshToken]:
    statement = select(RefreshToken).where(RefreshToken.family_id == family_id)
    return list(db.scalars(statement))
