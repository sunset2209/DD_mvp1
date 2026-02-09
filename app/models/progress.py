"""
Модели прогресса и попыток выполнения заданий.
"""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.task import Task


class TaskAttempt(Base, TimestampMixin):
    """
    Попытка выполнения задания.
    """

    __tablename__ = "task_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Связь с заданием
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False)
    task: Mapped["Task"] = relationship()

    # Связь с учеником
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    student: Mapped["Student"] = relationship()

    # Временные метки
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Результаты
    score: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0-100
    is_correct: Mapped[bool | None] = mapped_column(nullable=True)

    # Использованные подсказки
    hints_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Время выполнения (секунды)
    time_spent: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Ответы ученика
    answers: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    """
    Структура answers:
    {
        "selected": "A",  # или ["A", "B"] для множественного выбора
        "text": "Текстовый ответ",
        "steps": [...]  # для пошаговых заданий
    }
    """

    # Обратная связь
    feedback: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    """
    Структура feedback:
    {
        "message": "Отлично! Ты справился!",
        "detailed": "Объяснение...",
        "encouragement": "Продолжай в том же духе!",
    }
    """

    # Уровень скэффолдинга во время выполнения
    scaffolding_level_used: Mapped[int | None] = mapped_column(Integer, nullable=True)

    def __repr__(self) -> str:
        return f"TaskAttempt(id={self.id}, task_id={self.task_id}, score={self.score})"

    @property
    def is_completed(self) -> bool:
        """Проверить, завершена ли попытка."""
        return self.completed_at is not None
