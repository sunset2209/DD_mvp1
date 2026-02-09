"""
API эндпоинты пользователей.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import CurrentUserId, CurrentUserRole, DbSession, require_roles
from app.core.constants import UserRole
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user import UserService

router = APIRouter()


@router.get("/", response_model=list[UserResponse])
async def get_users(
    db: DbSession,
    _: Annotated[UserRole, Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER))],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    organization_id: int | None = None,
):
    """
    Получить список пользователей.

    Доступно только для администраторов и учителей.
    """
    service = UserService(db)
    return await service.get_all(skip=skip, limit=limit, organization_id=organization_id)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: DbSession,
    current_user_id: CurrentUserId,
    current_role: CurrentUserRole,
):
    """
    Получить пользователя по ID.

    Пользователи могут просматривать только себя.
    Администраторы и учителя могут просматривать всех.
    """
    # Проверка прав: пользователь может смотреть только себя
    if current_role not in (UserRole.ADMIN, UserRole.TEACHER) and user_id != current_user_id:
        from app.core.exceptions import ForbiddenException

        raise ForbiddenException("Нет доступа к этому пользователю")

    service = UserService(db)
    return await service.get_by_id(user_id)


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    data: UserCreate,
    db: DbSession,
    _: Annotated[UserRole, Depends(require_roles(UserRole.ADMIN))],
):
    """
    Создать пользователя.

    Доступно только для администраторов.
    """
    service = UserService(db)
    return await service.create(data)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: DbSession,
    current_user_id: CurrentUserId,
    current_role: CurrentUserRole,
):
    """
    Обновить пользователя.

    Пользователи могут обновлять только себя.
    Администраторы могут обновлять всех.
    """
    if current_role != UserRole.ADMIN and user_id != current_user_id:
        from app.core.exceptions import ForbiddenException

        raise ForbiddenException("Нет прав на обновление этого пользователя")

    service = UserService(db)
    return await service.update(user_id, data)


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    db: DbSession,
    _: Annotated[UserRole, Depends(require_roles(UserRole.ADMIN))],
):
    """
    Удалить пользователя.

    Доступно только для администраторов.
    """
    service = UserService(db)
    await service.delete(user_id)


@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: int,
    db: DbSession,
    _: Annotated[UserRole, Depends(require_roles(UserRole.ADMIN))],
):
    """
    Деактивировать пользователя.

    Доступно только для администраторов.
    """
    service = UserService(db)
    return await service.deactivate(user_id)
