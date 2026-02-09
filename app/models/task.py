"""
Модели заданий и шаблонов.
"""
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import DifficultyLevel, Subject, TaskStatus
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.iep import IEPGoal
    from app.models.student import Student
    from app.models.user import User


class TaskTemplate(Base, TimestampMixin):
    """
    Шаблон задания.
    Используется для генерации персонализированных заданий.
    """

    __tablename__ = "task_templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Предмет и тема
    subject: Mapped[Subject] = mapped_column(String(50), nullable=False)
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    subtopic: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Базовая сложность
    base_difficulty: Mapped[DifficultyLevel] = mapped_column(
        Integer, nullable=False, default=DifficultyLevel.MEDIUM
    )

    # Для каких типов ОВЗ подходит (пустой = для всех)
    disability_types: Mapped[list[str]] = mapped_column(
        ARRAY(String(50)), nullable=False, default=list
    )

    # Шаблон промпта для LLM
    prompt_template: Mapped[str] = mapped_column(Text, nullable=False)

    # Контент шаблона (базовая структура задания)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Флаги
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Автор шаблона
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_by: Mapped["User | None"] = relationship()

    # Классы, для которых подходит
    min_grade: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    max_grade: Mapped[int] = mapped_column(Integer, nullable=False, default=11)

    def __repr__(self) -> str:
        return f"TaskTemplate(id={self.id}, name={self.name}, subject={self.subject})"


class Task(Base, TimestampMixin):
    """
    Задание для ученика.
    Генерируется на основе шаблона с учётом профиля ученика.
    """

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    # Связь с шаблоном (опционально)
    template_id: Mapped[int | None] = mapped_column(
        ForeignKey("task_templates.id"), nullable=True
    )
    template: Mapped["TaskTemplate | None"] = relationship()

    # Связь с учеником
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    student: Mapped["Student"] = relationship()

    # Связь с целью ИОП (опционально)
    iep_goal_id: Mapped[int | None] = mapped_column(ForeignKey("iep_goals.id"), nullable=True)
    iep_goal: Mapped["IEPGoal | None"] = relationship()

    # Предмет и тема
    subject: Mapped[Subject] = mapped_column(String(50), nullable=False)
    topic: Mapped[str] = mapped_column(String(255), nullable=False)

    # Сложность (адаптированная под ученика)
    difficulty: Mapped[DifficultyLevel] = mapped_column(Integer, nullable=False)

    # Контент задания
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    """
    Структура content:
    {
        "type": "multiple_choice" | "fill_blank" | "matching" | "ordering" | "open_ended",
        "question": "Текст вопроса",
        "options": ["A", "B", "C", "D"],  # для multiple_choice
        "correct_answer": "A" | ["A", "B"] | {...},
        "hints": ["Подсказка 1", "Подсказка 2"],
        "explanation": "Объяснение правильного ответа",
        "media": {"image": "url", "audio": "url"},
    }
    """

    # Адаптации, применённые к заданию
    adaptations: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    """
    Структура adaptations:
    {
        "font_size": 18,
        "line_height": 1.8,
        "simplified_text": true,
        "audio_enabled": true,
        "extra_time": 30,
        "scaffolding_level": 2,
    }
    """

    # Статус
    status: Mapped[TaskStatus] = mapped_column(
        String(20), nullable=False, default=TaskStatus.ACTIVE
    )

    # Флаги
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Метаданные генерации (для XAI)
    generation_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    """
    Структура generation_metadata:
    {
        "model": "claude-3-haiku",
        "prompt_tokens": 500,
        "completion_tokens": 300,
        "reasoning": "Выбрано на основе профиля ученика...",
    }
    """

    def __repr__(self) -> str:
        return f"Task(id={self.id}, title={self.title}, student_id={self.student_id})"
