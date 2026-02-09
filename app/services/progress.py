"""
Сервис отслеживания прогресса и аналитики.
"""
from collections import defaultdict
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import DifficultyLevel, GoalStatus, Subject, TaskStatus
from app.core.exceptions import NotFoundException
from app.models.iep import IEP, IEPGoal
from app.models.progress import TaskAttempt
from app.models.task import Task
from app.schemas.progress import (
    DailyStats,
    GoalProgress,
    IEPProgress,
    ProgressSummary,
    StudentAnalytics,
    SubjectProgress,
    TaskRecommendation,
    WeeklyReport,
)


class ProgressService:
    """Сервис отслеживания прогресса."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_student_summary(self, student_id: int) -> ProgressSummary:
        """Получить сводку прогресса ученика."""
        # Общее количество заданий
        total_query = select(func.count(Task.id)).where(Task.student_id == student_id)
        total_result = await self.db.execute(total_query)
        total_tasks = total_result.scalar() or 0

        # Завершённые задания
        completed_query = select(func.count(Task.id)).where(
            Task.student_id == student_id,
            Task.status == TaskStatus.COMPLETED,
        )
        completed_result = await self.db.execute(completed_query)
        completed_tasks = completed_result.scalar() or 0

        # Статистика по попыткам
        attempts_query = select(
            func.count(TaskAttempt.id),
            func.sum(func.cast(TaskAttempt.is_correct, int)),
            func.avg(TaskAttempt.score),
            func.avg(TaskAttempt.time_spent),
            func.sum(TaskAttempt.hints_used),
        ).where(
            TaskAttempt.student_id == student_id,
            TaskAttempt.completed_at.isnot(None),
        )
        attempts_result = await self.db.execute(attempts_query)
        row = attempts_result.one()

        correct_answers = row[1] or 0
        average_score = float(row[2] or 0)
        average_time = float(row[3] or 0)
        total_hints = row[4] or 0

        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        return ProgressSummary(
            student_id=student_id,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            correct_answers=correct_answers,
            average_score=round(average_score, 2),
            average_time_spent=round(average_time, 2),
            total_hints_used=total_hints,
            completion_rate=round(completion_rate, 2),
        )

    async def get_subject_progress(
        self,
        student_id: int,
        subject: Subject,
    ) -> SubjectProgress:
        """Получить прогресс по предмету."""
        # Задания по предмету
        tasks_query = select(Task).where(
            Task.student_id == student_id,
            Task.subject == subject,
        )
        tasks_result = await self.db.execute(tasks_query)
        tasks = list(tasks_result.scalars().all())

        total = len(tasks)
        completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)

        # Темы
        topics = list({t.topic for t in tasks})

        # Статистика по попыткам
        task_ids = [t.id for t in tasks]
        if task_ids:
            attempts_query = select(
                TaskAttempt.task_id,
                func.avg(TaskAttempt.score),
            ).where(
                TaskAttempt.task_id.in_(task_ids),
                TaskAttempt.completed_at.isnot(None),
            ).group_by(TaskAttempt.task_id)
            attempts_result = await self.db.execute(attempts_query)
            scores_by_task = dict(attempts_result.all())

            # Определяем сильные и слабые темы
            topic_scores: dict[str, list[float]] = defaultdict(list)
            for task in tasks:
                if task.id in scores_by_task and scores_by_task[task.id]:
                    topic_scores[task.topic].append(float(scores_by_task[task.id]))

            weak_topics = []
            strong_topics = []
            for topic, scores in topic_scores.items():
                avg = sum(scores) / len(scores)
                if avg < 60:
                    weak_topics.append(topic)
                elif avg >= 80:
                    strong_topics.append(topic)

            overall_avg = sum(
                s for scores in topic_scores.values() for s in scores
            ) / max(1, sum(len(s) for s in topic_scores.values()))
        else:
            weak_topics = []
            strong_topics = []
            overall_avg = 0

        # Определяем текущую сложность
        current_difficulty = DifficultyLevel.MEDIUM
        if overall_avg >= 85:
            current_difficulty = DifficultyLevel.HARD
        elif overall_avg >= 70:
            current_difficulty = DifficultyLevel.MEDIUM
        elif overall_avg >= 50:
            current_difficulty = DifficultyLevel.EASY
        else:
            current_difficulty = DifficultyLevel.VERY_EASY

        return SubjectProgress(
            subject=subject,
            total_tasks=total,
            completed_tasks=completed,
            average_score=round(overall_avg, 2),
            current_difficulty=current_difficulty,
            topics_covered=topics,
            weak_topics=weak_topics,
            strong_topics=strong_topics,
        )

    async def get_iep_progress(self, student_id: int) -> IEPProgress | None:
        """Получить прогресс по ИОП."""
        # Находим активную ИОП
        iep_query = select(IEP).where(
            IEP.student_id == student_id,
            IEP.status == "active",
        )
        iep_result = await self.db.execute(iep_query)
        iep = iep_result.scalar_one_or_none()

        if not iep:
            return None

        # Получаем цели
        goals_query = select(IEPGoal).where(IEPGoal.iep_id == iep.id)
        goals_result = await self.db.execute(goals_query)
        goals = list(goals_result.scalars().all())

        total = len(goals)
        achieved = sum(1 for g in goals if g.status == GoalStatus.ACHIEVED)
        in_progress = sum(1 for g in goals if g.status == GoalStatus.IN_PROGRESS)
        not_started = sum(1 for g in goals if g.status == GoalStatus.NOT_STARTED)

        overall = (achieved / total * 100) if total > 0 else 0

        return IEPProgress(
            iep_id=iep.id,
            student_id=student_id,
            total_goals=total,
            achieved_goals=achieved,
            in_progress_goals=in_progress,
            not_started_goals=not_started,
            overall_progress=round(overall, 2),
        )

    async def get_goal_progress(self, goal_id: int) -> GoalProgress:
        """Получить прогресс по цели ИОП."""
        goal_query = select(IEPGoal).where(IEPGoal.id == goal_id)
        goal_result = await self.db.execute(goal_query)
        goal = goal_result.scalar_one_or_none()

        if not goal:
            raise NotFoundException("Цель не найдена")

        # Задания, связанные с целью
        tasks_query = select(Task).where(Task.iep_goal_id == goal_id)
        tasks_result = await self.db.execute(tasks_query)
        tasks = list(tasks_result.scalars().all())

        completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)

        # Средний балл по попыткам
        task_ids = [t.id for t in tasks]
        avg_score = 0.0
        last_activity = None

        if task_ids:
            attempts_query = select(
                func.avg(TaskAttempt.score),
                func.max(TaskAttempt.completed_at),
            ).where(
                TaskAttempt.task_id.in_(task_ids),
                TaskAttempt.completed_at.isnot(None),
            )
            attempts_result = await self.db.execute(attempts_query)
            row = attempts_result.one()
            avg_score = float(row[0] or 0)
            last_activity = row[1]

        return GoalProgress(
            goal_id=goal.id,
            goal_description=goal.description,
            status=GoalStatus(goal.status),
            current_progress=goal.current_progress or 0,
            target_value=goal.target_value or 100,
            tasks_completed=completed,
            average_score=round(avg_score, 2),
            last_activity=last_activity,
        )

    async def get_daily_stats(
        self,
        student_id: int,
        date: str,  # YYYY-MM-DD
    ) -> DailyStats:
        """Получить статистику за день."""
        from datetime import date as date_type

        target_date = date_type.fromisoformat(date)
        next_date = target_date + timedelta(days=1)

        # Попытки за день
        attempts_query = select(
            func.count(TaskAttempt.id),
            func.sum(func.cast(TaskAttempt.completed_at.isnot(None), int)),
            func.sum(func.cast(TaskAttempt.is_correct, int)),
            func.sum(TaskAttempt.time_spent),
            func.sum(TaskAttempt.hints_used),
        ).where(
            TaskAttempt.student_id == student_id,
            TaskAttempt.started_at >= datetime.combine(target_date, datetime.min.time()),
            TaskAttempt.started_at < datetime.combine(next_date, datetime.min.time()),
        )
        result = await self.db.execute(attempts_query)
        row = result.one()

        return DailyStats(
            date=date,
            tasks_attempted=row[0] or 0,
            tasks_completed=row[1] or 0,
            correct_answers=row[2] or 0,
            time_spent=row[3] or 0,
            hints_used=row[4] or 0,
        )

    async def get_weekly_report(
        self,
        student_id: int,
        week_start: str | None = None,
    ) -> WeeklyReport:
        """Получить недельный отчёт."""
        if week_start:
            from datetime import date as date_type
            start_date = date_type.fromisoformat(week_start)
        else:
            # Текущая неделя
            today = datetime.now(UTC).date()
            start_date = today - timedelta(days=today.weekday())

        end_date = start_date + timedelta(days=6)

        # Собираем статистику по дням
        daily_stats = []
        total_tasks = 0

        for i in range(7):
            day = start_date + timedelta(days=i)
            stats = await self.get_daily_stats(student_id, day.isoformat())
            daily_stats.append(stats)
            total_tasks += stats.tasks_completed

        avg_daily = total_tasks / 7

        # Определяем тренд (сравниваем первую и вторую половину недели)
        first_half = sum(s.tasks_completed for s in daily_stats[:4])
        second_half = sum(s.tasks_completed for s in daily_stats[4:])

        if second_half > first_half * 1.2:
            trend = "improving"
        elif second_half < first_half * 0.8:
            trend = "declining"
        else:
            trend = "stable"

        # Простые рекомендации
        recommendations = []
        if avg_daily < 2:
            recommendations.append("Попробуй выполнять хотя бы 2-3 задания в день")
        if trend == "declining":
            recommendations.append("Не сдавайся! Попробуй начать с более простых заданий")
        if trend == "improving":
            recommendations.append("Отличный прогресс! Продолжай в том же духе!")

        return WeeklyReport(
            student_id=student_id,
            week_start=start_date.isoformat(),
            week_end=end_date.isoformat(),
            daily_stats=daily_stats,
            total_tasks=total_tasks,
            average_daily_tasks=round(avg_daily, 2),
            improvement_trend=trend,
            recommendations=recommendations,
        )


class AnalyticsService:
    """Сервис аналитики."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.progress_service = ProgressService(db)

    async def get_full_analytics(self, student_id: int) -> StudentAnalytics:
        """Получить полную аналитику ученика."""
        # Базовая сводка
        summary = await self.progress_service.get_student_summary(student_id)

        # Прогресс по предметам
        subjects_progress = []
        for subject in Subject:
            progress = await self.progress_service.get_subject_progress(student_id, subject)
            if progress.total_tasks > 0:
                subjects_progress.append(progress)

        # Прогресс по ИОП
        iep_progress = await self.progress_service.get_iep_progress(student_id)

        # Определяем сильные стороны и области для улучшения
        strengths = []
        areas_for_improvement = []

        for sp in subjects_progress:
            if sp.average_score >= 80:
                strengths.append(f"{sp.subject}: отличные результаты")
            elif sp.average_score < 60:
                areas_for_improvement.append(f"{sp.subject}: требуется практика")

            strengths.extend([f"Тема: {t}" for t in sp.strong_topics[:2]])
            areas_for_improvement.extend([f"Тема: {t}" for t in sp.weak_topics[:2]])

        # Рекомендации по темам
        recommended_topics = []
        for sp in subjects_progress:
            recommended_topics.extend(sp.weak_topics[:1])

        # Рекомендация по скэффолдингу
        scaffolding_rec = 3
        if summary.average_score >= 85:
            scaffolding_rec = 4  # Меньше поддержки
        elif summary.average_score < 50:
            scaffolding_rec = 2  # Больше поддержки

        return StudentAnalytics(
            student_id=student_id,
            progress_summary=summary,
            subjects_progress=subjects_progress,
            iep_progress=iep_progress,
            skill_levels=[],  # TODO: реализовать систему навыков
            strengths=strengths[:5],
            areas_for_improvement=areas_for_improvement[:5],
            recommended_topics=recommended_topics[:5],
            scaffolding_recommendation=scaffolding_rec,
        )


class RecommendationEngine:
    """Рекомендательный движок."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.progress_service = ProgressService(db)

    async def get_recommendations(
        self,
        student_id: int,
        subject: Subject | None = None,
        limit: int = 5,
    ) -> list[TaskRecommendation]:
        """Получить рекомендации по заданиям."""
        recommendations = []

        # Определяем предметы для рекомендаций
        subjects = [subject] if subject else list(Subject)

        for subj in subjects:
            progress = await self.progress_service.get_subject_progress(student_id, subj)

            # Приоритет слабым темам
            for i, topic in enumerate(progress.weak_topics[:2]):
                recommendations.append(TaskRecommendation(
                    topic=topic,
                    subject=subj,
                    difficulty=DifficultyLevel.EASY,  # Начинаем с простого
                    reason=f"Требуется дополнительная практика по теме '{topic}'",
                    priority=10 - i,
                    estimated_time=10,
                ))

            # Если есть завершённые задания - предлагаем следующий уровень
            if progress.completed_tasks > 0 and progress.average_score >= 70:
                for topic in progress.strong_topics[:1]:
                    next_diff = DifficultyLevel(min(
                        progress.current_difficulty.value + 1, 5
                    ))
                    recommendations.append(TaskRecommendation(
                        topic=topic,
                        subject=subj,
                        difficulty=next_diff,
                        reason=f"Готов к более сложным заданиям по теме '{topic}'",
                        priority=5,
                        estimated_time=15,
                    ))

        # Сортируем по приоритету и ограничиваем
        recommendations.sort(key=lambda x: x.priority, reverse=True)
        return recommendations[:limit]
