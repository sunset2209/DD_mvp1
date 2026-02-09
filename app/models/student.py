"""
Модели ученика и профиля адаптации.
"""
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import DifficultyLevel, LearningStyle, ScaffoldingLevel
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.organization import Class
    from app.models.user import User


class Student(Base, TimestampMixin):
    """Ученик."""

    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Связь с пользователем (если ученик имеет аккаунт)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, unique=True)
    user: Mapped["User | None"] = relationship(foreign_keys=[user_id])

    # Связь с родителем
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    parent: Mapped["User | None"] = relationship(foreign_keys=[parent_id])

    # Связь с классом
    class_id: Mapped[int | None] = mapped_column(ForeignKey("classes.id"), nullable=True)
    student_class: Mapped["Class | None"] = relationship()

    # Данные ученика
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)

    # Профиль адаптации (один-к-одному)
    profile: Mapped["StudentProfile"] = relationship(
        back_populates="student", uselist=False, cascade="all, delete-orphan"
    )

    @property
    def full_name(self) -> str:
        """Полное имя ученика."""
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return " ".join(parts)

    def __repr__(self) -> str:
        return f"Student(id={self.id}, name={self.full_name}, grade={self.grade})"


class StudentProfile(Base, TimestampMixin):
    """
    Профиль адаптации ученика.
    Содержит настройки для персонализации заданий.
    """

    __tablename__ = "student_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Связь с учеником
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    student: Mapped["Student"] = relationship(back_populates="profile")

    # Типы ОВЗ (массив)
    disability_types: Mapped[list[str]] = mapped_column(
        ARRAY(String(50)), nullable=False, default=list
    )

    # Стиль обучения
    learning_style: Mapped[LearningStyle] = mapped_column(
        String(20), nullable=False, default=LearningStyle.VISUAL
    )

    # Уровень скэффолдинга по умолчанию
    scaffolding_level: Mapped[ScaffoldingLevel] = mapped_column(
        Integer, nullable=False, default=ScaffoldingLevel.MEDIUM_SUPPORT
    )

    # Текущий уровень сложности
    current_difficulty: Mapped[DifficultyLevel] = mapped_column(
        Integer, nullable=False, default=DifficultyLevel.EASY
    )

    # Настройки интерфейса
    font_size: Mapped[int] = mapped_column(Integer, nullable=False, default=16)
    line_height: Mapped[float] = mapped_column(nullable=False, default=1.5)
    color_scheme: Mapped[str] = mapped_column(String(50), nullable=False, default="default")
    audio_enabled: Mapped[bool] = mapped_column(nullable=False, default=True)
    animations_enabled: Mapped[bool] = mapped_column(nullable=False, default=True)

    # Темп работы (секунд на задание)
    preferred_pace: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Интересы для мотивации (JSON)
    interests: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Дополнительные настройки
    settings: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    def __repr__(self) -> str:
        return f"StudentProfile(id={self.id}, student_id={self.student_id})"
