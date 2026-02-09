"""
Сервис работы с заданиями и шаблонами.
"""
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.constants import Subject, TaskStatus
from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.progress import TaskAttempt
from app.models.task import Task, TaskTemplate
from app.schemas.task import (
    TaskAttemptCreate,
    TaskAttemptSubmit,
    TaskAttemptUpdate,
    TaskCreate,
    TaskTemplateCreate,
    TaskTemplateUpdate,
    TaskUpdate,
)


class TaskTemplateService:
    """Сервис шаблонов заданий."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, template_id: int) -> TaskTemplate:
        """Получить шаблон по ID."""
        result = await self.db.execute(
            select(TaskTemplate).where(TaskTemplate.id == template_id)
        )
        template = result.scalar_one_or_none()

        if not template:
            raise NotFoundException("Шаблон не найден")

        return template

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        subject: Subject | None = None,
        grade: int | None = None,
        disability_type: str | None = None,
        is_public: bool | None = None,
    ) -> list[TaskTemplate]:
        """Получить список шаблонов с фильтрацией."""
        query = select(TaskTemplate)

        if subject:
            query = query.where(TaskTemplate.subject == subject)
        if grade:
            query = query.where(
                TaskTemplate.min_grade <= grade,
                TaskTemplate.max_grade >= grade,
            )
        if disability_type:
            query = query.where(
                TaskTemplate.disability_types.contains([disability_type])
            )
        if is_public is not None:
            query = query.where(TaskTemplate.is_public == is_public)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def create(self, data: TaskTemplateCreate, created_by_id: int | None = None) -> TaskTemplate:
        """Создать шаблон."""
        template = TaskTemplate(
            **data.model_dump(),
            created_by_id=created_by_id,
        )

        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)

        return template

    async def update(self, template_id: int, data: TaskTemplateUpdate) -> TaskTemplate:
        """Обновить шаблон."""
        template = await self.get_by_id(template_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(template, field, value)

        await self.db.commit()
        await self.db.refresh(template)

        return template

    async def delete(self, template_id: int) -> None:
        """Удалить шаблон."""
        template = await self.get_by_id(template_id)
        await self.db.delete(template)
        await self.db.commit()


class TaskService:
    """Сервис заданий."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, task_id: int) -> Task:
        """Получить задание по ID."""
        result = await self.db.execute(
            select(Task)
            .options(selectinload(Task.template))
            .where(Task.id == task_id)
        )
        task = result.scalar_one_or_none()

        if not task:
            raise NotFoundException("Задание не найдено")

        return task

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        student_id: int | None = None,
        subject: Subject | None = None,
        status: TaskStatus | None = None,
        iep_goal_id: int | None = None,
    ) -> list[Task]:
        """Получить список заданий с фильтрацией."""
        query = select(Task)

        if student_id:
            query = query.where(Task.student_id == student_id)
        if subject:
            query = query.where(Task.subject == subject)
        if status:
            query = query.where(Task.status == status)
        if iep_goal_id:
            query = query.where(Task.iep_goal_id == iep_goal_id)

        query = query.order_by(Task.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def get_by_student(self, student_id: int, status: TaskStatus | None = None) -> list[Task]:
        """Получить задания ученика."""
        query = select(Task).where(Task.student_id == student_id)

        if status:
            query = query.where(Task.status == status)

        query = query.order_by(Task.created_at.desc())
        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def create(self, data: TaskCreate) -> Task:
        """Создать задание."""
        task = Task(**data.model_dump())

        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)

        return task

    async def update(self, task_id: int, data: TaskUpdate) -> Task:
        """Обновить задание."""
        task = await self.get_by_id(task_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        await self.db.commit()
        await self.db.refresh(task)

        return task

    async def delete(self, task_id: int) -> None:
        """Удалить задание."""
        task = await self.get_by_id(task_id)
        await self.db.delete(task)
        await self.db.commit()

    async def complete(self, task_id: int) -> Task:
        """Завершить задание."""
        task = await self.get_by_id(task_id)
        task.status = TaskStatus.COMPLETED
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def archive(self, task_id: int) -> Task:
        """Архивировать задание."""
        task = await self.get_by_id(task_id)
        task.status = TaskStatus.ARCHIVED
        await self.db.commit()
        await self.db.refresh(task)
        return task


class TaskAttemptService:
    """Сервис попыток выполнения заданий."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, attempt_id: int) -> TaskAttempt:
        """Получить попытку по ID."""
        result = await self.db.execute(
            select(TaskAttempt).where(TaskAttempt.id == attempt_id)
        )
        attempt = result.scalar_one_or_none()

        if not attempt:
            raise NotFoundException("Попытка не найдена")

        return attempt

    async def get_by_task(self, task_id: int) -> list[TaskAttempt]:
        """Получить все попытки по заданию."""
        result = await self.db.execute(
            select(TaskAttempt)
            .where(TaskAttempt.task_id == task_id)
            .order_by(TaskAttempt.started_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_student(
        self,
        student_id: int,
        limit: int = 100,
    ) -> list[TaskAttempt]:
        """Получить попытки ученика."""
        result = await self.db.execute(
            select(TaskAttempt)
            .where(TaskAttempt.student_id == student_id)
            .order_by(TaskAttempt.started_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def start_attempt(self, data: TaskAttemptCreate) -> TaskAttempt:
        """Начать новую попытку."""
        attempt = TaskAttempt(
            task_id=data.task_id,
            student_id=data.student_id,
            started_at=datetime.now(UTC),
            answers=data.answers,
            hints_used=data.hints_used,
            feedback={},
        )

        self.db.add(attempt)
        await self.db.commit()
        await self.db.refresh(attempt)

        return attempt

    async def submit_attempt(
        self,
        attempt_id: int,
        data: TaskAttemptSubmit,
        student_id: int,
    ) -> TaskAttempt:
        """Отправить ответ на задание."""
        attempt = await self.get_by_id(attempt_id)

        if attempt.student_id != student_id:
            raise ForbiddenException("Это не ваша попытка")

        if attempt.completed_at:
            raise ForbiddenException("Попытка уже завершена")

        attempt.answers = data.answers
        attempt.completed_at = datetime.now(UTC)
        attempt.time_spent = data.time_spent

        await self.db.commit()
        await self.db.refresh(attempt)

        return attempt

    async def update_attempt(self, attempt_id: int, data: TaskAttemptUpdate) -> TaskAttempt:
        """Обновить попытку (оценка, фидбэк)."""
        attempt = await self.get_by_id(attempt_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(attempt, field, value)

        await self.db.commit()
        await self.db.refresh(attempt)

        return attempt

    async def use_hint(self, attempt_id: int, student_id: int) -> TaskAttempt:
        """Использовать подсказку."""
        attempt = await self.get_by_id(attempt_id)

        if attempt.student_id != student_id:
            raise ForbiddenException("Это не ваша попытка")

        if attempt.completed_at:
            raise ForbiddenException("Попытка уже завершена")

        attempt.hints_used += 1
        await self.db.commit()
        await self.db.refresh(attempt)

        return attempt
