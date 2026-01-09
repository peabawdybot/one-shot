from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: UUID, task_data: TaskCreate) -> Task:
        task = Task(
            user_id=user_id,
            title=task_data.title,
            description=task_data.description,
        )
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def list_tasks(
        self,
        user_id: UUID,
        is_completed: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Task], int]:
        query = select(Task).where(Task.user_id == user_id)
        count_query = select(func.count(Task.id)).where(Task.user_id == user_id)

        if is_completed is not None:
            query = query.where(Task.is_completed == is_completed)
            count_query = count_query.where(Task.is_completed == is_completed)

        query = query.order_by(Task.created_at.desc()).limit(limit).offset(offset)

        result = await self.db.execute(query)
        tasks = list(result.scalars().all())

        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        return tasks, total

    async def get_by_id(self, task_id: UUID, user_id: UUID) -> Task | None:
        result = await self.db.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def update(self, task_id: UUID, user_id: UUID, task_data: TaskUpdate) -> Task | None:
        task = await self.get_by_id(task_id, user_id)
        if not task:
            return None

        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def delete(self, task_id: UUID, user_id: UUID) -> bool:
        task = await self.get_by_id(task_id, user_id)
        if not task:
            return False

        await self.db.delete(task)
        await self.db.commit()
        return True

    async def count_for_user(self, user_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count(Task.id)).where(Task.user_id == user_id)
        )
        return result.scalar() or 0
