from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin
from app.models.enums import ContributionGrade, PullRequestStatus, RejectCategory, Visibility


class PullRequest(TimestampMixin, Base):
    __tablename__ = "pull_requests"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id", ondelete="RESTRICT"), index=True, nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False)
    title: Mapped[str | None] = mapped_column(String(300))
    raw_content: Mapped[str | None] = mapped_column(Text(length=4_294_967_295))
    structured_content: Mapped[dict | None] = mapped_column(JSON)
    contribution_types: Mapped[list[str] | None] = mapped_column(JSON)
    visibility: Mapped[Visibility] = mapped_column(Enum(Visibility), default=Visibility.PUBLIC, nullable=False)
    status: Mapped[PullRequestStatus] = mapped_column(
        Enum(PullRequestStatus),
        default=PullRequestStatus.DRAFT,
        index=True,
        nullable=False,
    )
    author_grade_override: Mapped[ContributionGrade | None] = mapped_column(Enum(ContributionGrade))
    author_grade_override_reason: Mapped[str | None] = mapped_column(Text)
    author_review_comment: Mapped[str | None] = mapped_column(Text)
    changes_requested_reason: Mapped[str | None] = mapped_column(Text)
    contributor_comment: Mapped[str | None] = mapped_column(Text)
    first_drafted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_saved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    save_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    merged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    repository = relationship("Repository")
    author = relationship("User", back_populates="pull_requests")
    analyses = relationship("AiAnalysis", back_populates="pull_request")
    reject_reasons = relationship("RejectReason", back_populates="pull_request")
    view_logs = relationship("ViewLog", back_populates="pull_request")
    merge = relationship("Merge", back_populates="pull_request", uselist=False)


class RejectReason(Base):
    __tablename__ = "reject_reasons"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    pull_request_id: Mapped[int] = mapped_column(ForeignKey("pull_requests.id", ondelete="RESTRICT"), index=True, nullable=False)
    category: Mapped[RejectCategory] = mapped_column(Enum(RejectCategory), nullable=False)
    detail: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    superseded_by_id: Mapped[int | None] = mapped_column(ForeignKey("reject_reasons.id", ondelete="RESTRICT"))
    superseded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    pull_request = relationship("PullRequest", back_populates="reject_reasons")


class ViewLog(Base):
    __tablename__ = "view_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    pull_request_id: Mapped[int] = mapped_column(ForeignKey("pull_requests.id", ondelete="RESTRICT"), index=True, nullable=False)
    viewer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False)
    viewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ip_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    day_bucket_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    pull_request = relationship("PullRequest", back_populates="view_logs")

    __table_args__ = (
        UniqueConstraint("id", name="uq_view_logs_id"),
    )
