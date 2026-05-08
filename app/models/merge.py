from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.enums import ContributionGrade


class Merge(Base):
    __tablename__ = "merges"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    pull_request_id: Mapped[int] = mapped_column(ForeignKey("pull_requests.id", ondelete="RESTRICT"), unique=True, nullable=False)
    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id", ondelete="RESTRICT"), index=True, nullable=False)
    contributor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    final_grade: Mapped[ContributionGrade] = mapped_column(Enum(ContributionGrade), nullable=False)
    author_comment: Mapped[str | None] = mapped_column(Text)
    credit_text: Mapped[str] = mapped_column(String(500), nullable=False)
    readme_apply_note: Mapped[str | None] = mapped_column(Text)
    citation_url: Mapped[str] = mapped_column(String(500), nullable=False)
    merged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    pull_request = relationship("PullRequest", back_populates="merge")
