"""
Конфигурация приложения.
Использует pydantic-settings для загрузки переменных окружения.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/adaptive_learning"

    # JWT Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OpenRouter LLM
    OPENROUTER_API_KEY: str = ""
    DEFAULT_LLM_MODEL: str = "anthropic/claude-3-haiku"

    # App
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    LANGUAGE: str = "ru"
    APP_NAME: str = "Adaptive Learning API"
    APP_VERSION: str = "0.1.0"


@lru_cache
def get_settings() -> Settings:
    """Получить настройки приложения (кэшируется)."""
    return Settings()
