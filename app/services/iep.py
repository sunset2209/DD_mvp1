"""
Сервис работы с ИОП (Индивидуальными образовательными программами).
"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.models.iep import IEP, IEPGoal
from app.schemas.iep import IEPCreate, IEPGoalCreate, IEPGoalUpdate, IEPUpdate


class IEPService:
    """Сервис ИОП."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, iep_id: int) -> IEP:
        """Получить ИОП по ID с целями."""
        result = await self.db.execute(
            select(IEP).options(selectinload(IEP.goals)).where(IEP.id == iep_id)
        )
        iep = result.scalar_one_or_none()

        if not iep:
            raise NotFoundException("ИОП не найдена")

        return iep

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        student_id: int | None = None,
    ) -> list[IEP]:
        """Получить список ИОП."""
        query = select(IEP).options(selectinload(IEP.goals))

        if student_id:
            query = query.where(IEP.student_id == student_id)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def get_by_student(self, student_id: int) -> list[IEP]:
        """Получить все ИОП ученика."""
        return await self.get_all(student_id=student_id)

    async def create(self, data: IEPCreate, created_by_id: int) -> IEP:
        """Создать ИОП с целями."""
        # Создаём ИОП
        iep = IEP(
            title=data.title,
            description=data.description,
            student_id=data.student_id,
            created_by_id=created_by_id,
            start_date=data.start_date,
            end_date=data.end_date,
        )

        self.db.add(iep)
        await self.db.flush()

        # Создаём цели
        for goal_data in data.goals:
            goal = IEPGoal(
                iep_id=iep.id,
                subject=goal_data.subject,
                title=goal_data.title,
                description=goal_data.description,
                target_metric=goal_data.target_metric,
                target_value=goal_data.target_value,
                order=goal_data.order,
            )
            self.db.add(goal)

        await self.db.commit()

        return await self.get_by_id(iep.id)

    async def update(self, iep_id: int, data: IEPUpdate) -> IEP:
        """Обновить ИОП."""
        iep = await self.get_by_id(iep_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(iep, field, value)

        await self.db.commit()
        await self.db.refresh(iep)

        return iep

    async def delete(self, iep_id: int) -> None:
        """Удалить ИОП."""
        iep = await self.get_by_id(iep_id)
        await self.db.delete(iep)
        await self.db.commit()

    # Работа с целями

    async def add_goal(self, iep_id: int, data: IEPGoalCreate) -> IEPGoal:
        """Добавить цель в ИОП."""
        # Проверяем существование ИОП
        await self.get_by_id(iep_id)

        goal = IEPGoal(
            iep_id=iep_id,
            subject=data.subject,
            title=data.title,
            description=data.description,
            target_metric=data.target_metric,
            target_value=data.target_value,
            order=data.order,
        )

        self.db.add(goal)
        await self.db.commit()
        await self.db.refresh(goal)

        return goal

    async def get_goal(self, goal_id: int) -> IEPGoal:
        """Получить цель по ID."""
        result = await self.db.execute(select(IEPGoal).where(IEPGoal.id == goal_id))
        goal = result.scalar_one_or_none()

        if not goal:
            raise NotFoundException("Цель не найдена")

        return goal

    async def update_goal(self, goal_id: int, data: IEPGoalUpdate) -> IEPGoal:
        """Обновить цель."""
        goal = await self.get_goal(goal_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(goal, field, value)

        await self.db.commit()
        await self.db.refresh(goal)

        return goal

    async def delete_goal(self, goal_id: int) -> None:
        """Удалить цель."""
        goal = await self.get_goal(goal_id)
        await self.db.delete(goal)
        await self.db.commit()

    async def update_goal_progress(
        self,
        goal_id: int,
        current_value: float,
    ) -> IEPGoal:
        """Обновить прогресс по цели."""
        from app.core.constants import GoalStatus

        goal = await self.get_goal(goal_id)
        goal.current_value = current_value

        # Автоматически обновляем статус
        if current_value >= goal.target_value:
            goal.status = GoalStatus.ACHIEVED
        elif current_value > 0:
            goal.status = GoalStatus.IN_PROGRESS

        await self.db.commit()
        await self.db.refresh(goal)

        return goal
