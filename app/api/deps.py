"""
Зависимости для API эндпоинтов.
"""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UserRole
from app.core.security import decode_token
from app.database import get_db

# Схема авторизации Bearer
security = HTTPBearer()


async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> int:
    """
    Получить ID текущего пользователя из JWT токена.
    """
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
        )

    return int(user_id)


async def get_current_user_role(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> UserRole:
    """
    Получить роль текущего пользователя из JWT токена.
    """
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
        )

    role = payload.get("role")
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Роль не указана в токене",
        )

    return UserRole(role)


def require_roles(*roles: UserRole):
    """
    Фабрика зависимостей для проверки ролей.

    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(
            _: Annotated[UserRole, Depends(require_roles(UserRole.ADMIN))]
        ):
            ...
    """

    async def check_role(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    ) -> UserRole:
        token = credentials.credentials
        payload = decode_token(token)

        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный токен",
            )

        role = payload.get("role")
        if role is None or UserRole(role) not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав",
            )

        return UserRole(role)

    return check_role


# Type aliases для удобства
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUserId = Annotated[int, Depends(get_current_user_id)]
CurrentUserRole = Annotated[UserRole, Depends(get_current_user_role)]
