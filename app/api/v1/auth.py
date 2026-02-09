"""
API эндпоинты аутентификации.
"""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUserId, DbSession
from app.core.constants import UserRole
from app.schemas.auth import LoginRequest, RefreshTokenRequest, RegisterRequest, Token
from app.schemas.user import UserResponse
from app.services.auth import AuthService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    data: RegisterRequest,
    db: DbSession,
):
    """
    Регистрация нового пользователя.

    По умолчанию создаётся пользователь с ролью STUDENT.
    """
    service = AuthService(db)
    user = await service.register(data, role=UserRole.STUDENT)
    return user


@router.post("/register/teacher", response_model=UserResponse, status_code=201)
async def register_teacher(
    data: RegisterRequest,
    db: DbSession,
):
    """
    Регистрация учителя.
    """
    service = AuthService(db)
    user = await service.register(data, role=UserRole.TEACHER)
    return user


@router.post("/register/parent", response_model=UserResponse, status_code=201)
async def register_parent(
    data: RegisterRequest,
    db: DbSession,
):
    """
    Регистрация родителя.
    """
    service = AuthService(db)
    user = await service.register(data, role=UserRole.PARENT)
    return user


@router.post("/login", response_model=Token)
async def login(
    data: LoginRequest,
    db: DbSession,
):
    """
    Вход в систему.

    Возвращает access и refresh токены.
    """
    service = AuthService(db)
    return await service.login(data)


@router.post("/refresh", response_model=Token)
async def refresh_tokens(
    data: RefreshTokenRequest,
    db: DbSession,
):
    """
    Обновление токенов.

    Использует refresh токен для получения новой пары токенов.
    """
    service = AuthService(db)
    return await service.refresh_tokens(data.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: CurrentUserId,
    db: DbSession,
):
    """
    Получить данные текущего пользователя.
    """
    service = AuthService(db)
    return await service.get_current_user(user_id)
