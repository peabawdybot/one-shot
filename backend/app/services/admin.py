from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.user import User
from app.models.task import Task

class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_users(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict], int]:
        # Subquery for task count
        task_count_subq = (
            select(Task.user_id, func.count(Task.id).label("task_count"))
            .group_by(Task.user_id)
            .subquery()
        )

        # Main query joining users with task counts
        query = (
            select(User, func.coalesce(task_count_subq.c.task_count, 0).label("task_count"))
            .outerjoin(task_count_subq, User.id == task_count_subq.c.user_id)
            .order_by(User.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.db.execute(query)
        rows = result.all()

        users = []
        for row in rows:
            user = row[0]
            task_count = row[1]
            users.append({
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "last_login_at": user.last_login_at,
                "task_count": task_count,
            })

        # Total count
        count_result = await self.db.execute(select(func.count(User.id)))
        total = count_result.scalar() or 0

        return users, total

    async def get_user(self, user_id: UUID) -> dict | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            return None

        # Get task count
        count_result = await self.db.execute(
            select(func.count(Task.id)).where(Task.user_id == user_id)
        )
        task_count = count_result.scalar() or 0

        return {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "last_login_at": user.last_login_at,
            "task_count": task_count,
        }

    async def update_user_status(self, user_id: UUID, is_active: bool) -> dict | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            return None

        user.is_active = is_active
        await self.db.commit()
        await self.db.refresh(user)

        # Get task count
        count_result = await self.db.execute(
            select(func.count(Task.id)).where(Task.user_id == user_id)
        )
        task_count = count_result.scalar() or 0

        return {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "last_login_at": user.last_login_at,
            "task_count": task_count,
        }
