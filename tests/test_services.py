"""
Тесты сервисов.
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    DifficultyLevel,
    DisabilityType,
    LearningStyle,
    ScaffoldingLevel,
    Subject,
    TaskStatus,
)
from app.core.exceptions import NotFoundException
from app.models.student import Student, StudentProfile
from app.models.task import Task
from app.schemas.student import StudentCreate, StudentProfileCreate
from app.schemas.task import TaskCreate, TaskTemplateCreate
from app.services.student import StudentService
from app.services.task import TaskService, TaskTemplateService


class TestStudentService:
    """Тесты сервиса учеников."""

    @pytest.mark.asyncio
    async def test_create_student(self, db_session: AsyncSession):
        """Тест создания ученика через сервис."""
        service = StudentService(db_session)

        data = StudentCreate(
            first_name="Анна",
            last_name="Петрова",
            grade=4,
            profile=StudentProfileCreate(
                disability_types=[DisabilityType.DYSLEXIA],
                learning_style=LearningStyle.VISUAL,
                font_size=18,
            ),
        )

        student = await service.create(data)

        assert student.id is not None
        assert student.first_name == "Анна"
        assert student.profile is not None
        assert student.profile.font_size == 18

    @pytest.mark.asyncio
    async def test_get_student_by_id(self, db_session: AsyncSession):
        """Тест получения ученика по ID."""
        # Создаём ученика напрямую
        student = Student(first_name="Тест", last_name="Получения", grade=5)
        db_session.add(student)
        await db_session.flush()

        profile = StudentProfile(student_id=student.id)
        db_session.add(profile)
        await db_session.commit()

        # Получаем через сервис
        service = StudentService(db_session)
        found = await service.get_by_id(student.id)

        assert found.id == student.id
        assert found.first_name == "Тест"

    @pytest.mark.asyncio
    async def test_get_nonexistent_student(self, db_session: AsyncSession):
        """Тест получения несуществующего ученика."""
        service = StudentService(db_session)

        with pytest.raises(NotFoundException):
            await service.get_by_id(99999)


class TestTaskService:
    """Тесты сервиса заданий."""

    @pytest.mark.asyncio
    async def test_create_task(self, db_session: AsyncSession):
        """Тест создания задания."""
        # Создаём ученика
        student = Student(first_name="Задание", last_name="Тест", grade=3)
        db_session.add(student)
        await db_session.commit()

        service = TaskService(db_session)
        data = TaskCreate(
            title="Тестовое задание",
            student_id=student.id,
            subject=Subject.MATH,
            topic="Сложение",
            difficulty=DifficultyLevel.EASY,
            content={
                "type": "multiple_choice",
                "question": "2 + 2 = ?",
                "options": ["3", "4", "5"],
                "correct_answer": "4",
            },
        )

        task = await service.create(data)

        assert task.id is not None
        assert task.title == "Тестовое задание"
        assert task.status == TaskStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_get_tasks_by_student(self, db_session: AsyncSession):
        """Тест получения заданий ученика."""
        student = Student(first_name="Много", last_name="Заданий", grade=2)
        db_session.add(student)
        await db_session.flush()

        # Создаём несколько заданий
        for i in range(3):
            task = Task(
                title=f"Задание {i+1}",
                student_id=student.id,
                subject=Subject.RUSSIAN,
                topic="Буквы",
                difficulty=DifficultyLevel.EASY,
                content={"type": "multiple_choice", "question": "?"},
            )
            db_session.add(task)

        await db_session.commit()

        service = TaskService(db_session)
        tasks = await service.get_by_student(student.id)

        assert len(tasks) == 3

    @pytest.mark.asyncio
    async def test_complete_task(self, db_session: AsyncSession):
        """Тест завершения задания."""
        student = Student(first_name="Завершение", last_name="Тест", grade=1)
        db_session.add(student)
        await db_session.flush()

        task = Task(
            title="Для завершения",
            student_id=student.id,
            subject=Subject.MATH,
            topic="Счёт",
            difficulty=DifficultyLevel.VERY_EASY,
            content={"type": "fill_blank", "question": "1 + 1 = ?"},
        )
        db_session.add(task)
        await db_session.commit()

        service = TaskService(db_session)
        completed = await service.complete(task.id)

        assert completed.status == TaskStatus.COMPLETED


class TestTaskTemplateService:
    """Тесты сервиса шаблонов."""

    @pytest.mark.asyncio
    async def test_create_template(self, db_session: AsyncSession):
        """Тест создания шаблона."""
        service = TaskTemplateService(db_session)

        data = TaskTemplateCreate(
            name="Шаблон чтения",
            subject=Subject.READING,
            topic="Чтение вслух",
            prompt_template="Создай текст для чтения",
            content={"type": "open_ended"},
        )

        template = await service.create(data)

        assert template.id is not None
        assert template.name == "Шаблон чтения"
        assert template.is_public is True

    @pytest.mark.asyncio
    async def test_filter_templates_by_subject(self, db_session: AsyncSession):
        """Тест фильтрации шаблонов по предмету."""
        service = TaskTemplateService(db_session)

        # Создаём шаблоны разных предметов
        for subject in [Subject.MATH, Subject.MATH, Subject.RUSSIAN]:
            data = TaskTemplateCreate(
                name=f"Шаблон {subject}",
                subject=subject,
                topic="Тема",
                prompt_template="Промпт",
                content={},
            )
            await service.create(data)

        # Фильтруем
        math_templates = await service.get_all(subject=Subject.MATH)

        assert len(math_templates) == 2


class TestAdapters:
    """Тесты адаптеров."""

    def test_compute_adaptations_dyslexia(self):
        """Тест адаптаций для дислексии."""
        from app.services.generation.adapters import compute_adaptations

        result = compute_adaptations(
            disability_types=[DisabilityType.DYSLEXIA],
            learning_style=LearningStyle.VISUAL,
            scaffolding_level=ScaffoldingLevel.MEDIUM_SUPPORT,
        )

        assert result.font_size >= 18
        assert result.line_height >= 1.8
        assert result.audio_enabled is True
        assert result.extra_time >= 30

    def test_compute_adaptations_multiple_disabilities(self):
        """Тест адаптаций для нескольких ОВЗ."""
        from app.services.generation.adapters import compute_adaptations

        result = compute_adaptations(
            disability_types=[
                DisabilityType.DYSLEXIA,
                DisabilityType.ADHD,
                DisabilityType.VISUAL_IMPAIRED,
            ],
        )

        # Должен быть максимальный размер шрифта из всех адаптаций
        assert result.font_size >= 24  # Для нарушений зрения
        assert result.audio_enabled is True
        assert result.color_scheme == "high_contrast"

    def test_compute_adaptations_scaffolding(self):
        """Тест уровней скэффолдинга."""
        from app.services.generation.adapters import compute_adaptations

        full_support = compute_adaptations(
            disability_types=[],
            scaffolding_level=ScaffoldingLevel.FULL_SUPPORT,
        )

        independent = compute_adaptations(
            disability_types=[],
            scaffolding_level=ScaffoldingLevel.INDEPENDENT,
        )

        assert full_support.scaffolding_level == 1
        assert independent.scaffolding_level == 5
        assert len(full_support.content_modifications) > len(independent.content_modifications)
