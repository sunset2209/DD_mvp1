"""
Конфигурация pytest.
"""
import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from sqlalchemy import JSON
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models import Base

# Используем SQLite для тестов (in-memory)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Создать event loop для тестов."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


def convert_postgres_types_to_sqlite():
    """Конвертировать PostgreSQL типы в SQLite-совместимые."""
    from sqlalchemy.dialects.postgresql import ARRAY, JSONB

    # Заменяем JSONB и ARRAY на JSON для SQLite
    for table in Base.metadata.tables.values():
        for column in table.columns:
            if isinstance(column.type, JSONB):
                column.type = JSON()
            elif isinstance(column.type, ARRAY):
                # SQLite не поддерживает ARRAY, используем JSON
                column.type = JSON()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Создать тестовую сессию БД."""
    # Конвертируем типы PostgreSQL в SQLite-совместимые
    convert_postgres_types_to_sqlite()

    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()
