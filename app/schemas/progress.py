"""
Pydantic схемы для прогресса и аналитики.
"""
from datetime import datetime

from pydantic import BaseModel, Field

from app.core.constants import DifficultyLevel, GoalStatus, Subject


class ProgressSummary(BaseModel):
    """Сводка прогресса ученика."""

    student_id: int
    total_tasks: int = 0
    completed_tasks: int = 0
    correct_answers: int = 0
    average_score: float = 0.0
    average_time_spent: float = 0.0  # секунды
    total_hints_used: int = 0
    completion_rate: float = 0.0  # процент завершённых


class SubjectProgress(BaseModel):
    """Прогресс по предмету."""

    subject: Subject
    total_tasks: int = 0
    completed_tasks: int = 0
    average_score: float = 0.0
    current_difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    topics_covered: list[str] = []
    weak_topics: list[str] = []
    strong_topics: list[str] = []


class IEPProgress(BaseModel):
    """Прогресс по ИОП."""

    iep_id: int
    student_id: int
    total_goals: int = 0
    achieved_goals: int = 0
    in_progress_goals: int = 0
    not_started_goals: int = 0
    overall_progress: float = 0.0  # процент


class GoalProgress(BaseModel):
    """Прогресс по цели ИОП."""

    goal_id: int
    goal_description: str
    status: GoalStatus
    current_progress: float = 0.0
    target_value: float = 100.0
    tasks_completed: int = 0
    average_score: float = 0.0
    last_activity: datetime | None = None


class DailyStats(BaseModel):
    """Статистика за день."""

    date: str  # YYYY-MM-DD
    tasks_attempted: int = 0
    tasks_completed: int = 0
    correct_answers: int = 0
    time_spent: int = 0  # секунды
    hints_used: int = 0


class WeeklyReport(BaseModel):
    """Недельный отчёт."""

    student_id: int
    week_start: str  # YYYY-MM-DD
    week_end: str
    daily_stats: list[DailyStats] = []
    total_tasks: int = 0
    average_daily_tasks: float = 0.0
    improvement_trend: str = "stable"  # improving, declining, stable
    recommendations: list[str] = []


class SkillLevel(BaseModel):
    """Уровень навыка."""

    skill_name: str
    level: int = Field(..., ge=1, le=5)
    progress_to_next: float = 0.0  # процент до следующего уровня
    total_practice_time: int = 0  # минуты


class StudentAnalytics(BaseModel):
    """Полная аналитика ученика."""

    student_id: int
    progress_summary: ProgressSummary
    subjects_progress: list[SubjectProgress] = []
    iep_progress: IEPProgress | None = None
    skill_levels: list[SkillLevel] = []
    strengths: list[str] = []
    areas_for_improvement: list[str] = []
    recommended_topics: list[str] = []
    scaffolding_recommendation: int = 3


class RecommendationRequest(BaseModel):
    """Запрос рекомендаций."""

    student_id: int
    subject: Subject | None = None
    limit: int = Field(5, ge=1, le=20)


class TaskRecommendation(BaseModel):
    """Рекомендация задания."""

    topic: str
    subject: Subject
    difficulty: DifficultyLevel
    reason: str
    priority: int = Field(..., ge=1, le=10)
    estimated_time: int = 10  # минуты
