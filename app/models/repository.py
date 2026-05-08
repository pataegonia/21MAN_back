from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin


class Repository(TimestampMixin, Base):
    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500))
    external_links: Mapped[list[dict] | None] = mapped_column(JSON)
    readme_overview: Mapped[str | None] = mapped_column(Text)
    contribution_guideline: Mapped[str | None] = mapped_column(Text)

    author = relationship("User", back_populates="repositories")
    characters = relationship("RepoCharacter", back_populates="repository", cascade="all, delete-orphan")
    regions = relationship("RepoRegion", back_populates="repository", cascade="all, delete-orphan")
    rules = relationship("RepoRule", back_populates="repository", cascade="all, delete-orphan")
    forbidden_items = relationship("RepoForbidden", back_populates="repository", cascade="all, delete-orphan")
    recruiting_areas = relationship("RecruitingArea", back_populates="repository", cascade="all, delete-orphan")
    tags = relationship("RepositoryTag", back_populates="repository", cascade="all, delete-orphan")


class RepoStructuredItem(TimestampMixin):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(100))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class RepoCharacter(RepoStructuredItem, Base):
    __tablename__ = "repo_characters"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    repository = relationship("Repository", back_populates="characters")


class RepoRegion(RepoStructuredItem, Base):
    __tablename__ = "repo_regions"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    repository = relationship("Repository", back_populates="regions")


class RepoRule(RepoStructuredItem, Base):
    __tablename__ = "repo_rules"

    repository = relationship("Repository", back_populates="rules")


class RepoForbidden(RepoStructuredItem, Base):
    __tablename__ = "repo_forbidden"

    repository = relationship("Repository", back_populates="forbidden_items")


class RecruitingArea(RepoStructuredItem, Base):
    __tablename__ = "recruiting_areas"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    repository = relationship("Repository", back_populates="recruiting_areas")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    repositories = relationship("RepositoryTag", back_populates="tag")


class RepositoryTag(Base):
    __tablename__ = "repository_tags"

    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="RESTRICT"), primary_key=True, index=True)

    repository = relationship("Repository", back_populates="tags")
    tag = relationship("Tag", back_populates="repositories")
