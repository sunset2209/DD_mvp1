"""
API эндпоинты для прогресса и аналитики.
"""
from fastapi import APIRouter, Query

from app.api.deps import CurrentUserId, DbSession
from app.core.constants import Subject
from app.schemas.progress import (
    GoalProgress,
    IEPProgress,
    ProgressSummary,
    StudentAnalytics,
    SubjectProgress,
    TaskRecommendation,
    WeeklyReport,
)
from app.services.progress import AnalyticsService, ProgressService, RecommendationEngine

router = APIRouter()


# === Progress Endpoints ===

@router.get("/summary/{student_id}", response_model=ProgressSummary)
async def get_progress_summary(
    student_id: int,
    db: DbSession,
    _: CurrentUserId,
):
    """
    Получить сводку прогресса ученика.

    Включает:
    - Общее количество заданий
    - Завершённые задания
    - Средний балл
    - Среднее время выполнения
    """
    service = ProgressService(db)
    return await service.get_student_summary(student_id)


@router.get("/subject/{student_id}/{subject}", response_model=SubjectProgress)
async def get_subject_progress(
    student_id: int,
    subject: Subject,
    db: DbSession,
    _: CurrentUserId,
):
    """
    Получить прогресс по предмету.

    Включает:
    - Задания по предмету
    - Сильные и слабые темы
    - Рекомендуемый уровень сложности
    """
    service = ProgressService(db)
    return await service.get_subject_progress(student_id, subject)


@router.get("/iep/{student_id}", response_model=IEPProgress | None)
async def get_iep_progress(
    student_id: int,
    db: DbSession,
    _: CurrentUserId,
):
    """
    Получить прогресс по ИОП.

    Включает:
    - Количество целей по статусам
    - Общий процент выполнения
    """
    service = ProgressService(db)
    return await service.get_iep_progress(student_id)


@router.get("/goal/{goal_id}", response_model=GoalProgress)
async def get_goal_progress(
    goal_id: int,
    db: DbSession,
    _: CurrentUserId,
):
    """
    Получить прогресс по цели ИОП.

    Включает:
    - Текущий прогресс
    - Количество выполненных заданий
    - Средний балл
    """
    service = ProgressService(db)
    return await service.get_goal_progress(goal_id)


@router.get("/weekly/{student_id}", response_model=WeeklyReport)
async def get_weekly_report(
    student_id: int,
    db: DbSession,
    _: CurrentUserId,
    week_start: str | None = Query(None, description="Начало недели (YYYY-MM-DD)"),
):
    """
    Получить недельный отчёт.

    Включает:
    - Статистику по дням
    - Тренд улучшения
    - Рекомендации
    """
    service = ProgressService(db)
    return await service.get_weekly_report(student_id, week_start)


# === Analytics Endpoints ===

@router.get("/analytics/{student_id}", response_model=StudentAnalytics)
async def get_student_analytics(
    student_id: int,
    db: DbSession,
    _: CurrentUserId,
):
    """
    Получить полную аналитику ученика.

    Включает:
    - Сводку прогресса
    - Прогресс по предметам
    - Прогресс по ИОП
    - Сильные стороны и области для улучшения
    - Рекомендации
    """
    service = AnalyticsService(db)
    return await service.get_full_analytics(student_id)


# === Recommendations Endpoints ===

@router.get("/recommendations/{student_id}", response_model=list[TaskRecommendation])
async def get_recommendations(
    student_id: int,
    db: DbSession,
    _: CurrentUserId,
    subject: Subject | None = None,
    limit: int = Query(5, ge=1, le=20),
):
    """
    Получить персонализированные рекомендации.

    Учитывает:
    - Слабые темы ученика
    - Текущий уровень
    - Прогресс по предметам
    """
    engine = RecommendationEngine(db)
    return await engine.get_recommendations(student_id, subject, limit)
