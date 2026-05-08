"""add slug to repositories

Revision ID: a4c61472911c
Revises: 39038a4a6068
Create Date: 2026-05-09 04:30:38.021165
"""
import re
import secrets
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a4c61472911c"
down_revision: Union[str, None] = "39038a4a6068"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_SLUG_REPLACE = re.compile(r"[^a-z0-9가-힣]+")


def _slug_base(title: str) -> str:
    base = _SLUG_REPLACE.sub("-", (title or "").strip().lower()).strip("-")
    return (base or "repo")[:180]


def upgrade() -> None:
    op.add_column("repositories", sa.Column("slug", sa.String(length=200), nullable=True))

    conn = op.get_bind()
    rows = conn.execute(sa.text("SELECT id, title FROM repositories")).fetchall()
    for row in rows:
        slug = f"{_slug_base(row.title)}-{secrets.token_hex(4)}"
        conn.execute(
            sa.text("UPDATE repositories SET slug = :slug WHERE id = :id"),
            {"slug": slug, "id": row.id},
        )

    op.alter_column("repositories", "slug", existing_type=sa.String(length=200), nullable=False)
    op.create_index("ix_repositories_slug", "repositories", ["slug"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_repositories_slug", table_name="repositories")
    op.drop_column("repositories", "slug")
