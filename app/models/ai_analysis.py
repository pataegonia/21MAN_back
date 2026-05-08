from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.enums import ConflictRiskLevel, ContributionGrade


class AiAnalysis(Base):
    __tablename__ = "ai_analyses"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    pull_request_id: Mapped[int] = mapped_column(ForeignKey("pull_requests.id", ondelete="RESTRICT"), index=True, nullable=False)
    run_seq: Mapped[int] = mapped_column(Integer, nullable=False)
    generated_title: Mapped[str | None] = mapped_column(String(300))
    summary: Mapped[str | None] = mapped_column(Text)
    structured_content: Mapped[dict | None] = mapped_column(JSON)
    contribution_types: Mapped[list[str] | None] = mapped_column(JSON)
    score_scope: Mapped[int] = mapped_column(Integer, nullable=False)
    score_permanence: Mapped[int] = mapped_column(Integer, nullable=False)
    score_cascade: Mapped[int] = mapped_column(Integer, nullable=False)
    score_alignment: Mapped[int] = mapped_column(Integer, nullable=False)
    score_specificity: Mapped[int] = mapped_column(Integer, nullable=False)
    score_total: Mapped[int] = mapped_column(Integer, nullable=False)
    ai_grade: Mapped[ContributionGrade] = mapped_column(Enum(ContributionGrade), nullable=False)
    rationale: Mapped[str | None] = mapped_column(Text)
    missing_info: Mapped[list[str] | None] = mapped_column(JSON)
    model_name: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    pull_request = relationship("PullRequest", back_populates="analyses")
    conflict_checks = relationship("ConflictCheck", back_populates="ai_analysis")

    __table_args__ = (
        UniqueConstraint("pull_request_id", "run_seq", name="uq_ai_analyses_pr_run_seq"),
    )


class ConflictCheck(Base):
    __tablename__ = "conflict_checks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ai_analysis_id: Mapped[int] = mapped_column(ForeignKey("ai_analyses.id", ondelete="RESTRICT"), index=True, nullable=False)
    risk_level: Mapped[ConflictRiskLevel] = mapped_column(Enum(ConflictRiskLevel), nullable=False)
    check_target: Mapped[str] = mapped_column(String(50), nullable=False)
    target_ref_id: Mapped[int | None] = mapped_column(BigInteger)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    detail: Mapped[str | None] = mapped_column(Text)
    missing_info: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    ai_analysis = relationship("AiAnalysis", back_populates="conflict_checks")
