"""
Модели организаций и классов.
"""
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Organization(Base, TimestampMixin):
    """Организация (школа, центр)."""

    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False, default="school")
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    settings: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Связи
    users: Mapped[list["User"]] = relationship(back_populates="organization")
    classes: Mapped[list["Class"]] = relationship(back_populates="organization")

    def __repr__(self) -> str:
        return f"Organization(id={self.id}, name={self.name})"


class Class(Base, TimestampMixin):
    """Учебный класс."""

    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    academic_year: Mapped[str] = mapped_column(String(20), nullable=False)  # "2024-2025"

    # Связь с организацией
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    organization: Mapped["Organization"] = relationship(back_populates="classes")

    # Учитель класса
    teacher_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    def __repr__(self) -> str:
        return f"Class(id={self.id}, name={self.name}, grade={self.grade})"
