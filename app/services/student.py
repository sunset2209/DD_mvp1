"""
Сервис работы с учениками.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.models.student import Student, StudentProfile
from app.schemas.student import StudentCreate, StudentProfileUpdate, StudentUpdate


class StudentService:
    """Сервис учеников."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, student_id: int) -> Student:
        """Получить ученика по ID с профилем."""
        result = await self.db.execute(
            select(Student)
            .options(selectinload(Student.profile))
            .where(Student.id == student_id)
        )
        student = result.scalar_one_or_none()

        if not student:
            raise NotFoundException("Ученик не найден")

        return student

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        class_id: int | None = None,
        grade: int | None = None,
    ) -> list[Student]:
        """Получить список учеников."""
        query = select(Student).options(selectinload(Student.profile))

        if class_id:
            query = query.where(Student.class_id == class_id)
        if grade:
            query = query.where(Student.grade == grade)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def get_by_parent(self, parent_id: int) -> list[Student]:
        """Получить учеников родителя."""
        result = await self.db.execute(
            select(Student)
            .options(selectinload(Student.profile))
            .where(Student.parent_id == parent_id)
        )
        return list(result.scalars().all())

    async def create(self, data: StudentCreate) -> Student:
        """Создать ученика с профилем."""
        # Создаём ученика
        student = Student(
            first_name=data.first_name,
            last_name=data.last_name,
            middle_name=data.middle_name,
            birth_date=data.birth_date,
            grade=data.grade,
            parent_id=data.parent_id,
            class_id=data.class_id,
        )

        self.db.add(student)
        await self.db.flush()  # Получаем ID

        # Создаём профиль
        profile_data = data.profile or {}
        if isinstance(profile_data, dict):
            profile = StudentProfile(student_id=student.id, **profile_data)
        else:
            profile = StudentProfile(
                student_id=student.id,
                **profile_data.model_dump(),
            )

        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(student)

        # Загружаем профиль
        return await self.get_by_id(student.id)

    async def update(self, student_id: int, data: StudentUpdate) -> Student:
        """Обновить ученика."""
        student = await self.get_by_id(student_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(student, field, value)

        await self.db.commit()
        await self.db.refresh(student)

        return student

    async def delete(self, student_id: int) -> None:
        """Удалить ученика."""
        student = await self.get_by_id(student_id)
        await self.db.delete(student)
        await self.db.commit()

    async def get_profile(self, student_id: int) -> StudentProfile:
        """Получить профиль ученика."""
        student = await self.get_by_id(student_id)
        if not student.profile:
            raise NotFoundException("Профиль не найден")
        return student.profile

    async def update_profile(
        self,
        student_id: int,
        data: StudentProfileUpdate,
    ) -> StudentProfile:
        """Обновить профиль ученика."""
        student = await self.get_by_id(student_id)

        if not student.profile:
            # Создаём профиль, если не существует
            profile = StudentProfile(
                student_id=student_id,
                **data.model_dump(exclude_unset=True),
            )
            self.db.add(profile)
        else:
            # Обновляем существующий
            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(student.profile, field, value)

        await self.db.commit()
        await self.db.refresh(student)

        return student.profile
