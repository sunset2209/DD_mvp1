"""
Константы и перечисления (Enums) для приложения.
"""
from enum import Enum, StrEnum


class UserRole(StrEnum):
    """Роли пользователей в системе."""

    STUDENT = "student"
    PARENT = "parent"
    TEACHER = "teacher"
    TUTOR = "tutor"
    ADMIN = "admin"


class DisabilityType(StrEnum):
    """Типы особых образовательных потребностей (ОВЗ)."""

    DYSLEXIA = "dyslexia"  # Дислексия
    DYSCALCULIA = "dyscalculia"  # Дискалькулия
    DYSGRAPHIA = "dysgraphia"  # Дисграфия
    ADHD = "adhd"  # СДВГ
    ASD = "asd"  # РАС (аутизм)
    HEARING_IMPAIRED = "hearing"  # Нарушения слуха
    VISUAL_IMPAIRED = "visual"  # Нарушения зрения
    SPEECH_DISORDER = "speech"  # Нарушения речи
    INTELLECTUAL = "intellectual"  # Интеллектуальные нарушения
    MOTOR = "motor"  # Двигательные нарушения


class LearningStyle(StrEnum):
    """Стили обучения (способы восприятия информации)."""

    VISUAL = "visual"  # Визуальный
    AUDITORY = "auditory"  # Аудиальный
    KINESTHETIC = "kinesthetic"  # Кинестетический
    READING = "reading"  # Чтение/письмо


class DifficultyLevel(int, Enum):
    """Уровни сложности заданий."""

    VERY_EASY = 1
    EASY = 2
    MEDIUM = 3
    HARD = 4
    VERY_HARD = 5


class ScaffoldingLevel(int, Enum):
    """
    Уровни скэффолдинга (поддержки).
    От максимальной помощи до полной самостоятельности.
    """

    FULL_SUPPORT = 1  # Полная поддержка
    HIGH_SUPPORT = 2  # Высокая поддержка
    MEDIUM_SUPPORT = 3  # Средняя поддержка
    LOW_SUPPORT = 4  # Минимальная поддержка
    INDEPENDENT = 5  # Самостоятельно


class TaskStatus(StrEnum):
    """Статус задания."""

    DRAFT = "draft"  # Черновик
    ACTIVE = "active"  # Активное
    COMPLETED = "completed"  # Завершено
    ARCHIVED = "archived"  # В архиве


class IEPStatus(StrEnum):
    """Статус индивидуальной образовательной программы (ИОП)."""

    DRAFT = "draft"  # Черновик
    ACTIVE = "active"  # Активная
    COMPLETED = "completed"  # Завершена
    ARCHIVED = "archived"  # В архиве


class GoalStatus(StrEnum):
    """Статус цели в ИОП."""

    NOT_STARTED = "not_started"  # Не начата
    IN_PROGRESS = "in_progress"  # В процессе
    ACHIEVED = "achieved"  # Достигнута
    NOT_ACHIEVED = "not_achieved"  # Не достигнута


class Subject(StrEnum):
    """Учебные предметы."""

    RUSSIAN = "russian"  # Русский язык
    MATH = "math"  # Математика
    READING = "reading"  # Чтение/Литература
    NATURAL_SCIENCE = "natural_science"  # Окружающий мир
    ENGLISH = "english"  # Английский язык
    OTHER = "other"  # Другое
