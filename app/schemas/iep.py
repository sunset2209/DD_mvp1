"""
Pydantic схемы для ИОП (Индивидуальных образовательных программ).
"""
from datetime import date

from pydantic import BaseModel, Field

from app.core.constants import GoalStatus, IEPStatus, Subject


class IEPGoalBase(BaseModel):
    """Базовая схема цели ИОП."""

    subject: Subject
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    target_metric: str = Field(..., min_length=1, max_length=100)
    target_value: float = Field(..., gt=0)


class IEPGoalCreate(IEPGoalBase):
    """Схема создания цели."""

    order: int = 0


class IEPGoalUpdate(BaseModel):
    """Схема обновления цели."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    target_metric: str | None = None
    target_value: float | None = None
    current_value: float | None = None
    status: GoalStatus | None = None
    order: int | None = None


class IEPGoalResponse(IEPGoalBase):
    """Схема ответа с целью."""

    id: int
    iep_id: int
    current_value: float = 0
    status: GoalStatus = GoalStatus.NOT_STARTED
    order: int = 0
    progress_percent: float = 0

    model_config = {"from_attributes": True}


class IEPBase(BaseModel):
    """Базовая схема ИОП."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    start_date: date
    end_date: date


class IEPCreate(IEPBase):
    """Схема создания ИОП."""

    student_id: int
    goals: list[IEPGoalCreate] = []


class IEPUpdate(BaseModel):
    """Схема обновления ИОП."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: IEPStatus | None = None


class IEPResponse(IEPBase):
    """Схема ответа с ИОП."""

    id: int
    student_id: int
    created_by_id: int
    status: IEPStatus = IEPStatus.DRAFT
    goals: list[IEPGoalResponse] = []

    model_config = {"from_attributes": True}


class IEPListResponse(BaseModel):
    """Схема списка ИОП."""

    id: int
    title: str
    student_id: int
    status: IEPStatus
    start_date: date
    end_date: date
    goals_count: int = 0

    model_config = {"from_attributes": True}
