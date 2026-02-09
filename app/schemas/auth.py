"""
Pydantic схемы для аутентификации.
"""
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """Схема токенов."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Payload JWT токена."""

    sub: int  # user_id
    role: str
    exp: int
    type: str  # "access" | "refresh"


class LoginRequest(BaseModel):
    """Запрос на вход."""

    email: EmailStr
    password: str = Field(..., min_length=1)


class RegisterRequest(BaseModel):
    """Запрос на регистрацию."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    middle_name: str | None = Field(None, max_length=100)


class RefreshTokenRequest(BaseModel):
    """Запрос на обновление токена."""

    refresh_token: str
