"""
API эндпоинты ИОП (Индивидуальных образовательных программ).
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUserId, CurrentUserRole, DbSession, require_roles
from app.core.constants import UserRole
from app.core.exceptions import ForbiddenException
from app.schemas.iep import (
    IEPCreate,
    IEPGoalCreate,
    IEPGoalResponse,
    IEPGoalUpdate,
    IEPResponse,
    IEPUpdate,
)
from app.services.iep import IEPService
from app.services.student import StudentService

router = APIRouter()


@router.get("/", response_model=list[IEPResponse])
async def get_ieps(
    db: DbSession,
    current_role: CurrentUserRole,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    student_id: int | None = None,
):
    """
    Получить список ИОП.
    """
    if current_role not in (UserRole.ADMIN, UserRole.TEACHER, UserRole.TUTOR):
        raise ForbiddenException("Нет доступа к списку ИОП")

    service = IEPService(db)
    return await service.get_all(skip=skip, limit=limit, student_id=student_id)


@router.get("/student/{student_id}", response_model=list[IEPResponse])
async def get_student_ieps(
    student_id: int,
    db: DbSession,
    current_user_id: CurrentUserId,
    current_role: CurrentUserRole,
):
    """
    Получить все ИОП ученика.
    """
    # Проверка доступа для родителей
    if current_role == UserRole.PARENT:
        student_service = StudentService(db)
        student = await student_service.get_by_id(student_id)
        if student.parent_id != current_user_id:
            raise ForbiddenException("Нет доступа к ИОП этого ученика")

    service = IEPService(db)
    return await service.get_by_student(student_id)


@router.get("/{iep_id}", response_model=IEPResponse)
async def get_iep(
    iep_id: int,
    db: DbSession,
    current_user_id: CurrentUserId,
    current_role: CurrentUserRole,
):
    """
    Получить ИОП по ID.
    """
    service = IEPService(db)
    iep = await service.get_by_id(iep_id)

    # Проверка доступа для родителей
    if current_role == UserRole.PARENT:
        student_service = StudentService(db)
        student = await student_service.get_by_id(iep.student_id)
        if student.parent_id != current_user_id:
            raise ForbiddenException("Нет доступа к этой ИОП")

    return iep


@router.post("/", response_model=IEPResponse, status_code=201)
async def create_iep(
    data: IEPCreate,
    db: DbSession,
    current_user_id: CurrentUserId,
    _: Annotated[UserRole, Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER))],
):
    """
    Создать ИОП.

    Доступно для учителей и администраторов.
    """
    service = IEPService(db)
    return await service.create(data, created_by_id=current_user_id)


@router.put("/{iep_id}", response_model=IEPResponse)
async def update_iep(
    iep_id: int,
    data: IEPUpdate,
    db: DbSession,
    _: Annotated[UserRole, Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER))],
):
    """
    Обновить ИОП.
    """
    service = IEPService(db)
    return await service.update(iep_id, data)


@router.delete("/{iep_id}", status_code=204)
async def delete_iep(
    iep_id: int,
    db: DbSession,
    _: Annotated[UserRole, Depends(require_roles(UserRole.ADMIN))],
):
    """
    Удалить ИОП.
    """
    service = IEPService(db)
    await service.delete(iep_id)


# Работа с целями


@router.post("/{iep_id}/goals", response_model=IEPGoalResponse, status_code=201)
async def add_goal(
    iep_id: int,
    data: IEPGoalCreate,
    db: DbSession,
    _: Annotated[UserRole, Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER))],
):
    """
    Добавить цель в ИОП.
    """
    service = IEPService(db)
    return await service.add_goal(iep_id, data)


@router.put("/{iep_id}/goals/{goal_id}", response_model=IEPGoalResponse)
async def update_goal(
    iep_id: int,
    goal_id: int,
    data: IEPGoalUpdate,
    db: DbSession,
    _: Annotated[UserRole, Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER))],
):
    """
    Обновить цель ИОП.
    """
    service = IEPService(db)
    # Проверяем, что цель принадлежит ИОП
    goal = await service.get_goal(goal_id)
    if goal.iep_id != iep_id:
        raise ForbiddenException("Цель не принадлежит этой ИОП")

    return await service.update_goal(goal_id, data)


@router.delete("/{iep_id}/goals/{goal_id}", status_code=204)
async def delete_goal(
    iep_id: int,
    goal_id: int,
    db: DbSession,
    _: Annotated[UserRole, Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER))],
):
    """
    Удалить цель из ИОП.
    """
    service = IEPService(db)
    goal = await service.get_goal(goal_id)
    if goal.iep_id != iep_id:
        raise ForbiddenException("Цель не принадлежит этой ИОП")

    await service.delete_goal(goal_id)
