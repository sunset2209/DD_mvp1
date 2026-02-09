"""
Сервис работы с пользователями.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """Сервис пользователей."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> User:
        """Получить пользователя по ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundException("Пользователь не найден")

        return user

    async def get_by_email(self, email: str) -> User | None:
        """Получить пользователя по email."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        organization_id: int | None = None,
    ) -> list[User]:
        """Получить список пользователей."""
        query = select(User)

        if organization_id:
            query = query.where(User.organization_id == organization_id)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def create(self, data: UserCreate) -> User:
        """Создать пользователя."""
        user = User(
            email=data.email,
            hashed_password=get_password_hash(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
            middle_name=data.middle_name,
            role=data.role,
            is_active=True,
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def update(self, user_id: int, data: UserUpdate) -> User:
        """Обновить пользователя."""
        user = await self.get_by_id(user_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def delete(self, user_id: int) -> None:
        """Удалить пользователя."""
        user = await self.get_by_id(user_id)
        await self.db.delete(user)
        await self.db.commit()

    async def deactivate(self, user_id: int) -> User:
        """Деактивировать пользователя."""
        user = await self.get_by_id(user_id)
        user.is_active = False
        await self.db.commit()
        await self.db.refresh(user)
        return user
