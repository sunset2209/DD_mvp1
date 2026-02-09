"""
Pydantic схемы для учеников и профилей.
"""
from datetime import date

from pydantic import BaseModel, Field

from app.core.constants import DifficultyLevel, DisabilityType, LearningStyle, ScaffoldingLevel


class StudentProfileBase(BaseModel):
    """Базовая схема профиля ученика."""

    disability_types: list[DisabilityType] = []
    learning_style: LearningStyle = LearningStyle.VISUAL
    scaffolding_level: ScaffoldingLevel = ScaffoldingLevel.MEDIUM_SUPPORT
    current_difficulty: DifficultyLevel = DifficultyLevel.EASY
    font_size: int = Field(16, ge=12, le=32)
    line_height: float = Field(1.5, ge=1.0, le=3.0)
    color_scheme: str = "default"
    audio_enabled: bool = True
    animations_enabled: bool = True
    preferred_pace: int | None = None
    interests: dict = {}


class StudentProfileCreate(StudentProfileBase):
    """Схема создания профиля."""

    pass


class StudentProfileUpdate(BaseModel):
    """Схема обновления профиля."""

    disability_types: list[DisabilityType] | None = None
    learning_style: LearningStyle | None = None
    scaffolding_level: ScaffoldingLevel | None = None
    current_difficulty: DifficultyLevel | None = None
    font_size: int | None = Field(None, ge=12, le=32)
    line_height: float | None = Field(None, ge=1.0, le=3.0)
    color_scheme: str | None = None
    audio_enabled: bool | None = None
    animations_enabled: bool | None = None
    preferred_pace: int | None = None
    interests: dict | None = None


class StudentProfileResponse(StudentProfileBase):
    """Схема ответа с профилем."""

    id: int
    student_id: int

    model_config = {"from_attributes": True}


class StudentBase(BaseModel):
    """Базовая схема ученика."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    middle_name: str | None = Field(None, max_length=100)
    birth_date: date | None = None
    grade: int = Field(..., ge=1, le=11)


class StudentCreate(StudentBase):
    """Схема создания ученика."""

    parent_id: int | None = None
    class_id: int | None = None
    profile: StudentProfileCreate | None = None


class StudentUpdate(BaseModel):
    """Схема обновления ученика."""

    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    middle_name: str | None = None
    birth_date: date | None = None
    grade: int | None = Field(None, ge=1, le=11)
    parent_id: int | None = None
    class_id: int | None = None


class StudentResponse(StudentBase):
    """Схема ответа с данными ученика."""

    id: int
    user_id: int | None = None
    parent_id: int | None = None
    class_id: int | None = None
    profile: StudentProfileResponse | None = None

    model_config = {"from_attributes": True}


class StudentListResponse(BaseModel):
    """Схема списка учеников."""

    id: int
    first_name: str
    last_name: str
    grade: int
    class_id: int | None = None

    model_config = {"from_attributes": True}
