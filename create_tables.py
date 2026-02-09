"""Скрипт для создания таблиц (SQLite)."""
import asyncio
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from sqlalchemy.ext.asyncio import create_async_engine
from app.models import Base
from app.config import get_settings

settings = get_settings()


async def create_tables():
    """Создание всех таблиц."""
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()
    print("Таблицы созданы успешно!")


if __name__ == "__main__":
    asyncio.run(create_tables())
