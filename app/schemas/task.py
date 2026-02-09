"""
Pydantic схемы для заданий и шаблонов.
"""
from datetime import datetime

from pydantic import BaseModel, Field

from app.core.constants import DifficultyLevel, Subject, TaskStatus

# === TaskTemplate Schemas ===

class TaskTemplateBase(BaseModel):
    """Базовая схема шаблона задания."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    subject: Subject
    topic: str = Field(..., min_length=1, max_length=255)
    subtopic: str | None = Field(None, max_length=255)
    base_difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    disability_types: list[str] = []
    prompt_template: str
    content: dict = {}
    min_grade: int = Field(1, ge=1, le=11)
    max_grade: int = Field(11, ge=1, le=11)
    is_public: bool = True


class TaskTemplateCreate(TaskTemplateBase):
    """Схема создания шаблона."""

    pass


class TaskTemplateUpdate(BaseModel):
    """Схема обновления шаблона."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    subject: Subject | None = None
    topic: str | None = Field(None, min_length=1, max_length=255)
    subtopic: str | None = None
    base_difficulty: DifficultyLevel | None = None
    disability_types: list[str] | None = None
    prompt_template: str | None = None
    content: dict | None = None
    min_grade: int | None = Field(None, ge=1, le=11)
    max_grade: int | None = Field(None, ge=1, le=11)
    is_public: bool | None = None


class TaskTemplateResponse(TaskTemplateBase):
    """Схема ответа с шаблоном."""

    id: int
    is_ai_generated: bool
    created_by_id: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# === Task Schemas ===

class TaskContentBase(BaseModel):
    """Базовая схема контента задания."""

    type: str = Field(..., description="multiple_choice | fill_blank | matching | ordering | open_ended")
    question: str
    options: list[str] | None = None
    correct_answer: str | list | dict | None = None
    hints: list[str] = []
    explanation: str | None = None
    media: dict | None = None


class TaskAdaptationsBase(BaseModel):
    """Базовая схема адаптаций задания."""

    font_size: int | None = None
    line_height: float | None = None
    simplified_text: bool | None = None
    audio_enabled: bool | None = None
    extra_time: int | None = None
    scaffolding_level: int | None = None


class TaskBase(BaseModel):
    """Базовая схема задания."""

    title: str = Field(..., min_length=1, max_length=255)
    subject: Subject
    topic: str = Field(..., min_length=1, max_length=255)
    difficulty: DifficultyLevel
    content: dict
    adaptations: dict = {}


class TaskCreate(TaskBase):
    """Схема создания задания."""

    student_id: int
    template_id: int | None = None
    iep_goal_id: int | None = None
    is_ai_generated: bool = False
    generation_metadata: dict = {}


class TaskUpdate(BaseModel):
    """Схема обновления задания."""

    title: str | None = Field(None, min_length=1, max_length=255)
    subject: Subject | None = None
    topic: str | None = None
    difficulty: DifficultyLevel | None = None
    content: dict | None = None
    adaptations: dict | None = None
    status: TaskStatus | None = None


class TaskResponse(TaskBase):
    """Схема ответа с заданием."""

    id: int
    student_id: int
    template_id: int | None = None
    iep_goal_id: int | None = None
    status: TaskStatus
    is_ai_generated: bool
    generation_metadata: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    """Схема списка заданий."""

    id: int
    title: str
    subject: Subject
    topic: str
    difficulty: DifficultyLevel
    status: TaskStatus
    student_id: int
    is_ai_generated: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# === TaskAttempt Schemas ===

class TaskAttemptBase(BaseModel):
    """Базовая схема попытки выполнения."""

    answers: dict = {}
    hints_used: int = 0


class TaskAttemptCreate(TaskAttemptBase):
    """Схема создания попытки."""

    task_id: int
    student_id: int


class TaskAttemptSubmit(BaseModel):
    """Схема отправки ответа."""

    answers: dict
    time_spent: int | None = None


class TaskAttemptUpdate(BaseModel):
    """Схема обновления попытки."""

    answers: dict | None = None
    hints_used: int | None = None
    score: float | None = Field(None, ge=0, le=100)
    is_correct: bool | None = None
    feedback: dict | None = None


class TaskAttemptResponse(BaseModel):
    """Схема ответа с попыткой."""

    id: int
    task_id: int
    student_id: int
    started_at: datetime
    completed_at: datetime | None = None
    score: float | None = None
    is_correct: bool | None = None
    hints_used: int
    time_spent: int | None = None
    answers: dict
    feedback: dict
    scaffolding_level_used: int | None = None

    model_config = {"from_attributes": True}
