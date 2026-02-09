"""
Сервис аутентификации.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UserRole
from app.core.exceptions import BadRequestException, ConflictException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, Token


class AuthService:
    """Сервис аутентификации."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, data: RegisterRequest, role: UserRole = UserRole.STUDENT) -> User:
        """
        Регистрация нового пользователя.

        Args:
            data: Данные для регистрации
            role: Роль пользователя

        Returns:
            Созданный пользователь

        Raises:
            ConflictException: Если email уже занят
        """
        # Проверяем, не занят ли email
        existing = await self.db.execute(select(User).where(User.email == data.email))
        if existing.scalar_one_or_none():
            raise ConflictException("Пользователь с таким email уже существует")

        # Создаём пользователя
        user = User(
            email=data.email,
            hashed_password=get_password_hash(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
            middle_name=data.middle_name,
            role=role,
            is_active=True,
            is_verified=False,
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def login(self, data: LoginRequest) -> Token:
        """
        Вход пользователя.

        Args:
            data: Email и пароль

        Returns:
            Access и refresh токены

        Raises:
            UnauthorizedException: Неверные учётные данные
        """
        # Ищем пользователя
        result = await self.db.execute(select(User).where(User.email == data.email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedException("Неверный email или пароль")

        if not user.is_active:
            raise UnauthorizedException("Аккаунт деактивирован")

        # Создаём токены
        token_data = {"sub": user.id, "role": user.role.value}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    async def refresh_tokens(self, refresh_token: str) -> Token:
        """
        Обновление токенов по refresh token.

        Args:
            refresh_token: Refresh токен

        Returns:
            Новая пара токенов

        Raises:
            UnauthorizedException: Невалидный refresh токен
        """
        payload = decode_token(refresh_token)

        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedException("Невалидный refresh токен")

        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Невалидный refresh токен")

        # Проверяем, существует ли пользователь
        result = await self.db.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise UnauthorizedException("Пользователь не найден или деактивирован")

        # Создаём новые токены
        token_data = {"sub": user.id, "role": user.role.value}
        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)

        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
        )

    async def get_current_user(self, user_id: int) -> User:
        """
        Получить текущего пользователя по ID.

        Args:
            user_id: ID пользователя

        Returns:
            Пользователь

        Raises:
            UnauthorizedException: Пользователь не найден
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise UnauthorizedException("Пользователь не найден")

        return user
