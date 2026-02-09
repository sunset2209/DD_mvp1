"""
API эндпоинты учеников.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUserId, CurrentUserRole, DbSession, require_roles
from app.core.constants import UserRole
from app.core.exceptions import ForbiddenException
from app.schemas.student import (
    StudentCreate,
    StudentListResponse,
    StudentProfileResponse,
    StudentProfileUpdate,
    StudentResponse,
    StudentUpdate,
)
from app.services.student import StudentService

router = APIRouter()


@router.get("/", response_model=list[StudentListResponse])
async def get_students(
    db: DbSession,
    _: Annotated[UserRole, Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER, UserRole.TUTOR))],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    class_id: int | None = None,
    grade: int | None = None,
):
    """
    Получить список учеников.

    Доступно для учителей, тьюторов и администраторов.
    """
    service = StudentService(db)
    return await service.get_all(skip=skip, limit=limit, class_id=class_id, grade=grade)


@router.get("/my-children", response_model=list[StudentResponse])
async def get_my_children(
    db: DbSession,
    current_user_id: CurrentUserId,
    current_role: CurrentUserRole,
):
    """
    Получить своих детей (для родителей).
    """
    if current_role != UserRole.PARENT:
        raise ForbiddenException("Доступно только для родителей")

    service = StudentService(db)
    return await service.get_by_parent(current_user_id)


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: int,
    db: DbSession,
    current_user_id: CurrentUserId,
    current_role: CurrentUserRole,
):
    """
    Получить ученика по ID.
    """
    service = StudentService(db)
    student = await service.get_by_id(student_id)

    # Проверка доступа: родитель может видеть только своих детей
    if current_role == UserRole.PARENT and student.parent_id != current_user_id:
        raise ForbiddenException("Нет доступа к этому ученику")

    return student


@router.post("/", response_model=StudentResponse, status_code=201)
async def create_student(
    data: StudentCreate,
    db: DbSession,
    _: Annotated[UserRole, Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER))],
):
    """
    Создать ученика.

    Доступно для учителей и администраторов.
    """
    service = StudentService(db)
    return await service.create(data)


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    data: StudentUpdate,
    db: DbSession,
    _: Annotated[UserRole, Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER))],
):
    """
    Обновить ученика.
    """
    service = StudentService(db)
    return await service.update(student_id, data)


@router.delete("/{student_id}", status_code=204)
async def delete_student(
    student_id: int,
    db: DbSession,
    _: Annotated[UserRole, Depends(require_roles(UserRole.ADMIN))],
):
    """
    Удалить ученика.

    Доступно только для администраторов.
    """
    service = StudentService(db)
    await service.delete(student_id)


@router.get("/{student_id}/profile", response_model=StudentProfileResponse)
async def get_student_profile(
    student_id: int,
    db: DbSession,
    current_user_id: CurrentUserId,
    current_role: CurrentUserRole,
):
    """
    Получить профиль адаптации ученика.
    """
    service = StudentService(db)
    student = await service.get_by_id(student_id)

    # Проверка доступа
    if current_role == UserRole.PARENT and student.parent_id != current_user_id:
        raise ForbiddenException("Нет доступа к профилю этого ученика")

    return await service.get_profile(student_id)


@router.put("/{student_id}/profile", response_model=StudentProfileResponse)
async def update_student_profile(
    student_id: int,
    data: StudentProfileUpdate,
    db: DbSession,
    current_user_id: CurrentUserId,
    current_role: CurrentUserRole,
):
    """
    Обновить профиль адаптации ученика.
    """
    service = StudentService(db)
    student = await service.get_by_id(student_id)

    # Родитель может обновлять профиль своего ребёнка
    if current_role == UserRole.PARENT and student.parent_id != current_user_id:
        raise ForbiddenException("Нет доступа к профилю этого ученика")
    elif current_role not in (UserRole.ADMIN, UserRole.TEACHER, UserRole.TUTOR, UserRole.PARENT):
        raise ForbiddenException("Нет прав на изменение профиля")

    return await service.update_profile(student_id, data)
