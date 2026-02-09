"""
Pydantic схемы для пользователей.
"""
from pydantic import BaseModel, EmailStr, Field

from app.core.constants import UserRole


class UserBase(BaseModel):
    """Базовая схема пользователя."""

    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    middle_name: str | None = Field(None, max_length=100)


class UserCreate(UserBase):
    """Схема создания пользователя."""

    password: str = Field(..., min_length=8, max_length=100)
    role: UserRole = UserRole.STUDENT


class UserUpdate(BaseModel):
    """Схема обновления пользователя."""

    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    middle_name: str | None = Field(None, max_length=100)
    is_active: bool | None = None


class UserResponse(UserBase):
    """Схема ответа с данными пользователя."""

    id: int
    role: UserRole
    is_active: bool
    is_verified: bool
    organization_id: int | None = None

    model_config = {"from_attributes": True}


class UserInDB(UserResponse):
    """Схема пользователя из БД (с хешем пароля)."""

    hashed_password: str
