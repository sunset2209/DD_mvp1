"""
Pydantic схемы для заданий и генерации.
"""
from pydantic import BaseModel, Field

from app.core.constants import DifficultyLevel, DisabilityType, Subject


class TaskGenerateRequest(BaseModel):
    """Запрос на генерацию задания."""

    student_id: int
    subject: Subject
    topic: str = Field(..., min_length=1, max_length=255)
    difficulty: DifficultyLevel | None = None  # Если None, определится автоматически
    iep_goal_id: int | None = None  # Привязка к цели ИОП


class TaskAdaptRequest(BaseModel):
    """Запрос на адаптацию существующего задания."""

    task_id: int
    disability_types: list[DisabilityType] = []
    scaffolding_level: int | None = None


class TaskContent(BaseModel):
    """Контент задания."""

    type: str = Field(..., description="Тип: multiple_choice, fill_blank, matching, etc.")
    question: str
    options: list[str] | None = None
    correct_answer: str | list[str] | dict | None = None
    hints: list[str] = []
    explanation: str | None = None
    media: dict | None = None


class TaskAdaptations(BaseModel):
    """Адаптации задания."""

    font_size: int = 16
    line_height: float = 1.5
    simplified_text: bool = False
    audio_enabled: bool = True
    extra_time: int = 0  # Дополнительное время в секундах
    scaffolding_level: int = 3


class GeneratedTask(BaseModel):
    """Сгенерированное задание."""

    title: str
    subject: Subject
    topic: str
    difficulty: DifficultyLevel
    content: TaskContent
    adaptations: TaskAdaptations
    generation_metadata: dict = {}


class GenerationExplanation(BaseModel):
    """Объяснение выбора параметров генерации (XAI)."""

    reasoning: str
    factors: list[str]
    student_profile_considered: dict
    alternative_suggestions: list[str] = []
