"""
Главный роутер API v1.
"""
from fastapi import APIRouter

from app.api.v1 import auth, generation, iep, progress, students, tasks, users

api_router = APIRouter()


@api_router.get("/ping", tags=["Health"])
async def ping():
    """Проверка доступности API."""
    return {"ping": "pong"}


# Подключаем роутеры
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(students.router, prefix="/students", tags=["Students"])
api_router.include_router(iep.router, prefix="/iep", tags=["IEP"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(generation.router, prefix="/generate", tags=["Generation"])
api_router.include_router(progress.router, prefix="/progress", tags=["Progress"])
