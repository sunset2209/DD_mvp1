"""
Тесты моделей.
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import (
    DifficultyLevel,
    DisabilityType,
    GoalStatus,
    IEPStatus,
    LearningStyle,
    ScaffoldingLevel,
    Subject,
    TaskStatus,
    UserRole,
)
from app.models.iep import IEP, IEPGoal
from app.models.student import Student, StudentProfile
from app.models.task import Task, TaskTemplate
from app.models.user import User


class TestUserModel:
    """Тесты модели пользователя."""

    @pytest.mark.asyncio
    async def test_create_user(self, db_session: AsyncSession):
        """Тест создания пользователя."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123",
            role=UserRole.TEACHER,
            first_name="Иван",
            last_name="Иванов",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.role == UserRole.TEACHER
        assert user.is_active is True

    @pytest.mark.asyncio
    async def test_user_roles(self, db_session: AsyncSession):
        """Тест различных ролей пользователей."""
        roles = [UserRole.STUDENT, UserRole.PARENT, UserRole.TEACHER, UserRole.ADMIN]

        for i, role in enumerate(roles):
            user = User(
                email=f"user{i}@example.com",
                hashed_password="hash",
                role=role,
                first_name=f"Имя{i}",
                last_name=f"Фамилия{i}",
            )
            db_session.add(user)

        await db_session.commit()

        # Проверяем, что все пользователи созданы
        from sqlalchemy import select
        result = await db_session.execute(select(User))
        users = result.scalars().all()

        assert len(users) == 4


class TestStudentModel:
    """Тесты модели ученика."""

    @pytest.mark.asyncio
    async def test_create_student(self, db_session: AsyncSession):
        """Тест создания ученика."""
        student = Student(
            first_name="Петя",
            last_name="Петров",
            grade=3,
        )
        db_session.add(student)
        await db_session.commit()
        await db_session.refresh(student)

        assert student.id is not None
        assert student.first_name == "Петя"
        assert student.grade == 3

    @pytest.mark.asyncio
    async def test_create_student_profile(self, db_session: AsyncSession):
        """Тест создания профиля ученика."""
        student = Student(
            first_name="Маша",
            last_name="Сидорова",
            grade=5,
        )
        db_session.add(student)
        await db_session.flush()

        profile = StudentProfile(
            student_id=student.id,
            disability_types=[DisabilityType.DYSLEXIA, DisabilityType.ADHD],
            learning_style=LearningStyle.VISUAL,
            scaffolding_level=ScaffoldingLevel.HIGH_SUPPORT,
            current_difficulty=DifficultyLevel.EASY,
            font_size=20,
            audio_enabled=True,
        )
        db_session.add(profile)
        await db_session.commit()

        assert profile.id is not None
        assert DisabilityType.DYSLEXIA in profile.disability_types
        assert profile.learning_style == LearningStyle.VISUAL
        assert profile.font_size == 20


class TestIEPModel:
    """Тесты модели ИОП."""

    @pytest.mark.asyncio
    async def test_create_iep(self, db_session: AsyncSession):
        """Тест создания ИОП."""
        from datetime import date, timedelta

        # Создаём пользователя (учитель)
        teacher = User(
            email="teacher@test.com",
            hashed_password="hash",
            role=UserRole.TEACHER,
            first_name="Учитель",
            last_name="Тестов",
        )
        db_session.add(teacher)
        await db_session.flush()

        # Создаём ученика
        student = Student(first_name="Тест", last_name="Учения", grade=4)
        db_session.add(student)
        await db_session.flush()

        # Создаём ИОП
        iep = IEP(
            student_id=student.id,
            created_by_id=teacher.id,
            title="ИОП на 2024 год",
            description="Индивидуальная программа обучения",
            status=IEPStatus.ACTIVE,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
        )
        db_session.add(iep)
        await db_session.commit()

        assert iep.id is not None
        assert iep.status == IEPStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_create_iep_goal(self, db_session: AsyncSession):
        """Тест создания цели ИОП."""
        from datetime import date, timedelta

        # Создаём пользователя
        teacher = User(
            email="teacher2@test.com",
            hashed_password="hash",
            role=UserRole.TEACHER,
            first_name="Учитель",
            last_name="Целей",
        )
        db_session.add(teacher)
        await db_session.flush()

        student = Student(first_name="Тест", last_name="Цели", grade=2)
        db_session.add(student)
        await db_session.flush()

        iep = IEP(
            student_id=student.id,
            created_by_id=teacher.id,
            title="Тестовая ИОП",
            status=IEPStatus.ACTIVE,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=180),
        )
        db_session.add(iep)
        await db_session.flush()

        goal = IEPGoal(
            iep_id=iep.id,
            title="Скорость чтения",
            description="Научиться читать со скоростью 60 слов/мин",
            subject=Subject.READING,
            target_metric="слов в минуту",
            target_value=60,
            current_value=45,
            status=GoalStatus.IN_PROGRESS,
        )
        db_session.add(goal)
        await db_session.commit()

        assert goal.id is not None
        assert goal.current_value == 45
        assert goal.status == GoalStatus.IN_PROGRESS


class TestTaskModel:
    """Тесты модели заданий."""

    @pytest.mark.asyncio
    async def test_create_task_template(self, db_session: AsyncSession):
        """Тест создания шаблона задания."""
        template = TaskTemplate(
            name="Шаблон сложения",
            description="Шаблон для генерации заданий на сложение",
            subject=Subject.MATH,
            topic="Сложение чисел",
            base_difficulty=DifficultyLevel.EASY,
            prompt_template="Создай задачу на сложение двух чисел до {max_number}",
            content={"type": "fill_blank", "template": "{a} + {b} = ?"},
            min_grade=1,
            max_grade=4,
        )
        db_session.add(template)
        await db_session.commit()

        assert template.id is not None
        assert template.subject == Subject.MATH
        assert template.is_public is True

    @pytest.mark.asyncio
    async def test_create_task(self, db_session: AsyncSession):
        """Тест создания задания."""
        student = Student(first_name="Тест", last_name="Задания", grade=3)
        db_session.add(student)
        await db_session.flush()

        task = Task(
            title="Сложение: 5 + 3",
            student_id=student.id,
            subject=Subject.MATH,
            topic="Сложение",
            difficulty=DifficultyLevel.EASY,
            content={
                "type": "fill_blank",
                "question": "5 + 3 = ?",
                "correct_answer": "8",
                "hints": ["Посчитай на пальцах"],
            },
            adaptations={
                "font_size": 20,
                "audio_enabled": True,
            },
            status=TaskStatus.ACTIVE,
        )
        db_session.add(task)
        await db_session.commit()

        assert task.id is not None
        assert task.content["correct_answer"] == "8"
        assert task.adaptations["font_size"] == 20


class TestConstants:
    """Тесты констант и перечислений."""

    def test_disability_types(self):
        """Тест типов ОВЗ."""
        assert DisabilityType.DYSLEXIA == "dyslexia"
        assert DisabilityType.DYSCALCULIA == "dyscalculia"
        assert DisabilityType.ADHD == "adhd"
        assert DisabilityType.ASD == "asd"

    def test_difficulty_levels(self):
        """Тест уровней сложности."""
        assert DifficultyLevel.VERY_EASY.value == 1
        assert DifficultyLevel.MEDIUM.value == 3
        assert DifficultyLevel.VERY_HARD.value == 5

    def test_scaffolding_levels(self):
        """Тест уровней скэффолдинга."""
        assert ScaffoldingLevel.FULL_SUPPORT.value == 1
        assert ScaffoldingLevel.INDEPENDENT.value == 5

    def test_learning_styles(self):
        """Тест стилей обучения."""
        assert LearningStyle.VISUAL == "visual"
        assert LearningStyle.AUDITORY == "auditory"
        assert LearningStyle.KINESTHETIC == "kinesthetic"
