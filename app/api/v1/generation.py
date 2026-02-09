"""
API эндпоинты для генерации заданий.
"""
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUserId, DbSession, require_roles
from app.core.constants import UserRole
from app.schemas.generation import (
    GeneratedTask,
    GenerationExplanation,
    TaskAdaptRequest,
    TaskGenerateRequest,
)
from app.services.generation.generator import TaskGenerator
from app.services.task import TaskService

router = APIRouter()


@router.post("/task", response_model=GeneratedTask)
async def generate_task(
    data: TaskGenerateRequest,
    db: DbSession,
    _: Annotated[UserRole, Depends(require_roles(UserRole.TEACHER, UserRole.TUTOR, UserRole.ADMIN))],
):
    """
    Сгенерировать адаптивное задание для ученика.

    Генерирует задание с учётом:
    - Профиля ученика (ОВЗ, стиль обучения)
    - Уровня скэффолдинга
    - Текущего уровня сложности
    - Привязки к цели ИОП (если указана)
    """
    generator = TaskGenerator(db)
    return await generator.generate_task(
        student_id=data.student_id,
        subject=data.subject,
        topic=data.topic,
        difficulty=data.difficulty,
        iep_goal_id=data.iep_goal_id,
    )


@router.post("/adapt")
async def adapt_task(
    data: TaskAdaptRequest,
    db: DbSession,
    _: Annotated[UserRole, Depends(require_roles(UserRole.TEACHER, UserRole.TUTOR, UserRole.ADMIN))],
):
    """
    Адаптировать существующее задание под профиль ученика.

    Применяет адаптации на основе:
    - Типов ОВЗ ученика
    - Стиля обучения
    - Уровня скэффолдинга
    - Настроек доступности из профиля
    """
    # Получаем задание
    task_service = TaskService(db)
    task = await task_service.get_by_id(data.task_id)

    generator = TaskGenerator(db)

    # Если указаны конкретные типы ОВЗ, используем их
    # Иначе берём из профиля ученика
    return await generator.adapt_existing_task(
        task=task,
        student_id=task.student_id,
    )


@router.post("/explain", response_model=GenerationExplanation)
async def explain_recommendation(
    student_id: int,
    task_id: int,
    db: DbSession,
    _: CurrentUserId,
):
    """
    Объяснить, почему рекомендовано данное задание (XAI).

    Возвращает:
    - Причины выбора задания
    - Факторы, учтённые при генерации
    - Альтернативные предложения
    """
    task_service = TaskService(db)
    task = await task_service.get_by_id(task_id)

    task_info = {
        "title": task.title,
        "subject": task.subject,
        "topic": task.topic,
        "difficulty": task.difficulty.value if task.difficulty else 3,
    }

    generator = TaskGenerator(db)
    return await generator.explain_recommendation(
        student_id=student_id,
        task_info=task_info,
    )


@router.post("/feedback")
async def generate_feedback(
    task_id: int,
    student_answer: str,
    hints_used: int = 0,
    time_spent: int | None = None,
    db: DbSession = None,
    _: CurrentUserId = None,
):
    """
    Сгенерировать персонализированную обратную связь.

    Учитывает:
    - Правильность ответа
    - Количество использованных подсказок
    - Время выполнения
    - Профиль ученика
    """
    task_service = TaskService(db)
    task = await task_service.get_by_id(task_id)

    # Проверяем ответ
    correct_answer = task.content.get("correct_answer", "")
    is_correct = str(student_answer).lower().strip() == str(correct_answer).lower().strip()

    generator = TaskGenerator(db)
    return await generator.generate_feedback(
        task_title=task.title,
        correct_answer=str(correct_answer),
        student_answer=student_answer,
        is_correct=is_correct,
        hints_used=hints_used,
        time_spent=time_spent,
        student_id=task.student_id,
    )


@router.post("/task/save", status_code=201)
async def generate_and_save_task(
    data: TaskGenerateRequest,
    db: DbSession,
    _: Annotated[UserRole, Depends(require_roles(UserRole.TEACHER, UserRole.TUTOR, UserRole.ADMIN))],
):
    """
    Сгенерировать задание и сразу сохранить в базу.

    Возвращает сохранённое задание с ID.
    """
    from app.schemas.task import TaskCreate

    generator = TaskGenerator(db)
    generated = await generator.generate_task(
        student_id=data.student_id,
        subject=data.subject,
        topic=data.topic,
        difficulty=data.difficulty,
        iep_goal_id=data.iep_goal_id,
    )

    # Сохраняем в базу
    task_service = TaskService(db)
    task_data = TaskCreate(
        title=generated.title,
        student_id=data.student_id,
        subject=generated.subject,
        topic=generated.topic,
        difficulty=generated.difficulty,
        content=generated.content.model_dump(),
        adaptations=generated.adaptations.model_dump(),
        iep_goal_id=data.iep_goal_id,
        is_ai_generated=True,
        generation_metadata=generated.generation_metadata,
    )

    task = await task_service.create(task_data)

    return {
        "task_id": task.id,
        "generated": generated.model_dump(),
    }
