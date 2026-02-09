"""
API эндпоинты для заданий и шаблонов.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUserId, CurrentUserRole, DbSession, require_roles
from app.core.constants import Subject, TaskStatus, UserRole
from app.schemas.task import (
    TaskAttemptCreate,
    TaskAttemptResponse,
    TaskAttemptSubmit,
    TaskAttemptUpdate,
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskTemplateCreate,
    TaskTemplateResponse,
    TaskTemplateUpdate,
    TaskUpdate,
)
from app.services.task import TaskAttemptService, TaskService, TaskTemplateService

router = APIRouter()


# === Task Templates ===

@router.get("/templates", response_model=list[TaskTemplateResponse])
async def get_templates(
    db: DbSession,
    _: CurrentUserId,  # требуется авторизация
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    subject: Subject | None = None,
    grade: int | None = Query(None, ge=1, le=11),
    disability_type: str | None = None,
    is_public: bool | None = None,
):
    """Получить список шаблонов заданий."""
    service = TaskTemplateService(db)
    return await service.get_all(
        skip=skip,
        limit=limit,
        subject=subject,
        grade=grade,
        disability_type=disability_type,
        is_public=is_public,
    )


@router.get("/templates/{template_id}", response_model=TaskTemplateResponse)
async def get_template(
    template_id: int,
    db: DbSession,
    _: CurrentUserId,
):
    """Получить шаблон по ID."""
    service = TaskTemplateService(db)
    return await service.get_by_id(template_id)


@router.post("/templates", response_model=TaskTemplateResponse, status_code=201)
async def create_template(
    data: TaskTemplateCreate,
    db: DbSession,
    user_id: CurrentUserId,
    _: Annotated[UserRole, Depends(require_roles(UserRole.TEACHER, UserRole.ADMIN))],
):
    """Создать шаблон задания (только учитель/админ)."""
    service = TaskTemplateService(db)
    return await service.create(data, created_by_id=user_id)


@router.patch("/templates/{template_id}", response_model=TaskTemplateResponse)
async def update_template(
    template_id: int,
    data: TaskTemplateUpdate,
    db: DbSession,
    _: Annotated[UserRole, Depends(require_roles(UserRole.TEACHER, UserRole.ADMIN))],
):
    """Обновить шаблон (только учитель/админ)."""
    service = TaskTemplateService(db)
    return await service.update(template_id, data)


@router.delete("/templates/{template_id}", status_code=204)
async def delete_template(
    template_id: int,
    db: DbSession,
    _: Annotated[UserRole, Depends(require_roles(UserRole.ADMIN))],
):
    """Удалить шаблон (только админ)."""
    service = TaskTemplateService(db)
    await service.delete(template_id)


# === Tasks ===

@router.get("", response_model=list[TaskListResponse])
async def get_tasks(
    db: DbSession,
    _: CurrentUserId,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    student_id: int | None = None,
    subject: Subject | None = None,
    status: TaskStatus | None = None,
    iep_goal_id: int | None = None,
):
    """Получить список заданий."""
    service = TaskService(db)
    return await service.get_all(
        skip=skip,
        limit=limit,
        student_id=student_id,
        subject=subject,
        status=status,
        iep_goal_id=iep_goal_id,
    )


@router.get("/student/{student_id}", response_model=list[TaskListResponse])
async def get_student_tasks(
    student_id: int,
    db: DbSession,
    _: CurrentUserId,
    status: TaskStatus | None = None,
):
    """Получить задания ученика."""
    service = TaskService(db)
    return await service.get_by_student(student_id, status=status)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: DbSession,
    _: CurrentUserId,
):
    """Получить задание по ID."""
    service = TaskService(db)
    return await service.get_by_id(task_id)


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    data: TaskCreate,
    db: DbSession,
    _: Annotated[UserRole, Depends(require_roles(UserRole.TEACHER, UserRole.TUTOR, UserRole.ADMIN))],
):
    """Создать задание (учитель/тьютор/админ)."""
    service = TaskService(db)
    return await service.create(data)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    db: DbSession,
    _: Annotated[UserRole, Depends(require_roles(UserRole.TEACHER, UserRole.TUTOR, UserRole.ADMIN))],
):
    """Обновить задание."""
    service = TaskService(db)
    return await service.update(task_id, data)


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    db: DbSession,
    _: Annotated[UserRole, Depends(require_roles(UserRole.TEACHER, UserRole.ADMIN))],
):
    """Удалить задание."""
    service = TaskService(db)
    await service.delete(task_id)


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: int,
    db: DbSession,
    _: Annotated[UserRole, Depends(require_roles(UserRole.TEACHER, UserRole.TUTOR, UserRole.ADMIN))],
):
    """Завершить задание."""
    service = TaskService(db)
    return await service.complete(task_id)


@router.post("/{task_id}/archive", response_model=TaskResponse)
async def archive_task(
    task_id: int,
    db: DbSession,
    _: Annotated[UserRole, Depends(require_roles(UserRole.TEACHER, UserRole.ADMIN))],
):
    """Архивировать задание."""
    service = TaskService(db)
    return await service.archive(task_id)


# === Task Attempts ===

@router.get("/{task_id}/attempts", response_model=list[TaskAttemptResponse])
async def get_task_attempts(
    task_id: int,
    db: DbSession,
    _: CurrentUserId,
):
    """Получить все попытки по заданию."""
    service = TaskAttemptService(db)
    return await service.get_by_task(task_id)


@router.post("/{task_id}/attempts", response_model=TaskAttemptResponse, status_code=201)
async def start_attempt(
    task_id: int,
    db: DbSession,
    user_id: CurrentUserId,
    role: CurrentUserRole,
):
    """Начать новую попытку выполнения задания."""
    # Получаем задание для проверки и получения student_id
    task_service = TaskService(db)
    task = await task_service.get_by_id(task_id)

    # Проверка доступа: ученик может начать попытку только своего задания
    # или учитель/родитель может начать демо-попытку
    if role == UserRole.STUDENT:
        # Здесь нужно получить student_id по user_id
        # Пока используем student_id из задания
        student_id = task.student_id
    else:
        student_id = task.student_id

    data = TaskAttemptCreate(
        task_id=task_id,
        student_id=student_id,
    )

    service = TaskAttemptService(db)
    return await service.start_attempt(data)


@router.post("/attempts/{attempt_id}/submit", response_model=TaskAttemptResponse)
async def submit_attempt(
    attempt_id: int,
    data: TaskAttemptSubmit,
    db: DbSession,
    user_id: CurrentUserId,
):
    """Отправить ответ на задание."""
    # Получаем попытку для получения student_id
    service = TaskAttemptService(db)
    attempt = await service.get_by_id(attempt_id)

    return await service.submit_attempt(attempt_id, data, attempt.student_id)


@router.patch("/attempts/{attempt_id}", response_model=TaskAttemptResponse)
async def update_attempt(
    attempt_id: int,
    data: TaskAttemptUpdate,
    db: DbSession,
    _: Annotated[UserRole, Depends(require_roles(UserRole.TEACHER, UserRole.TUTOR, UserRole.ADMIN))],
):
    """Обновить попытку (оценка, фидбэк) - только учитель/тьютор/админ."""
    service = TaskAttemptService(db)
    return await service.update_attempt(attempt_id, data)


@router.post("/attempts/{attempt_id}/hint", response_model=TaskAttemptResponse)
async def use_hint(
    attempt_id: int,
    db: DbSession,
    user_id: CurrentUserId,
):
    """Использовать подсказку."""
    service = TaskAttemptService(db)
    attempt = await service.get_by_id(attempt_id)

    return await service.use_hint(attempt_id, attempt.student_id)


@router.get("/attempts/student/{student_id}", response_model=list[TaskAttemptResponse])
async def get_student_attempts(
    student_id: int,
    db: DbSession,
    _: CurrentUserId,
    limit: int = Query(100, ge=1, le=100),
):
    """Получить попытки ученика."""
    service = TaskAttemptService(db)
    return await service.get_by_student(student_id, limit=limit)
