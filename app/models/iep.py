"""
Модели индивидуальной образовательной программы (ИОП).
"""
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import GoalStatus, IEPStatus, Subject
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.user import User


class IEP(Base, TimestampMixin):
    """
    Индивидуальная образовательная программа (ИОП).
    """

    __tablename__ = "ieps"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Связь с учеником
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    student: Mapped["Student"] = relationship()

    # Кто создал
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_by: Mapped["User"] = relationship()

    # Период действия
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Статус
    status: Mapped[IEPStatus] = mapped_column(
        String(20), nullable=False, default=IEPStatus.DRAFT
    )

    # Цели ИОП
    goals: Mapped[list["IEPGoal"]] = relationship(
        back_populates="iep", cascade="all, delete-orphan"
    )

    # Дополнительные данные
    extra_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    def __repr__(self) -> str:
        return f"IEP(id={self.id}, student_id={self.student_id}, status={self.status})"


class IEPGoal(Base, TimestampMixin):
    """
    Цель в ИОП.
    """

    __tablename__ = "iep_goals"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Связь с ИОП
    iep_id: Mapped[int] = mapped_column(
        ForeignKey("ieps.id", ondelete="CASCADE"), nullable=False
    )
    iep: Mapped["IEP"] = relationship(back_populates="goals")

    # Предмет
    subject: Mapped[Subject] = mapped_column(String(50), nullable=False)

    # Описание цели
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Метрики
    target_metric: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # Например: "правильных ответов %"
    target_value: Mapped[float] = mapped_column(Float, nullable=False)  # Целевое значение
    current_value: Mapped[float] = mapped_column(Float, nullable=False, default=0)  # Текущее

    # Статус
    status: Mapped[GoalStatus] = mapped_column(
        String(20), nullable=False, default=GoalStatus.NOT_STARTED
    )

    # Порядок отображения
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        return f"IEPGoal(id={self.id}, subject={self.subject}, status={self.status})"

    @property
    def progress_percent(self) -> float:
        """Прогресс в процентах."""
        if self.target_value == 0:
            return 0
        return min(100, (self.current_value / self.target_value) * 100)
