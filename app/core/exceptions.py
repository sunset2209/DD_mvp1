"""
Кастомные исключения приложения.
"""
from fastapi import HTTPException, status


class AppException(HTTPException):
    """Базовое исключение приложения."""

    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = "Внутренняя ошибка сервера",
    ):
        super().__init__(status_code=status_code, detail=detail)


class NotFoundException(AppException):
    """Ресурс не найден."""

    def __init__(self, detail: str = "Ресурс не найден"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UnauthorizedException(AppException):
    """Неавторизованный доступ."""

    def __init__(self, detail: str = "Необходима авторизация"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenException(AppException):
    """Доступ запрещён."""

    def __init__(self, detail: str = "Доступ запрещён"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class BadRequestException(AppException):
    """Неверный запрос."""

    def __init__(self, detail: str = "Неверный запрос"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class ConflictException(AppException):
    """Конфликт данных."""

    def __init__(self, detail: str = "Конфликт данных"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class ValidationException(AppException):
    """Ошибка валидации."""

    def __init__(self, detail: str = "Ошибка валидации данных"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


class LLMException(AppException):
    """Ошибка при работе с LLM."""

    def __init__(self, detail: str = "Ошибка генерации через LLM"):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)
