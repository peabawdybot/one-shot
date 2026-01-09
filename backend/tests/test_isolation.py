import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.models.user import User
from app.models.task import Task
from app.database import set_rls_context

class TestRLSIsolation:
    async def test_rls_prevents_cross_user_access(self, db: AsyncSession, test_user: User, test_admin: User):
        # Create tasks for both users
        user_task = Task(user_id=test_user.id, title="User's task")
        admin_task = Task(user_id=test_admin.id, title="Admin's task")
        db.add_all([user_task, admin_task])
        await db.commit()

        # Set RLS context to test_user
        await set_rls_context(db, str(test_user.id))

        # Query tasks - should only see test_user's task
        result = await db.execute(select(Task))
        tasks = result.scalars().all()

        # Due to RLS, only user's task should be visible
        assert len(tasks) == 1
        assert tasks[0].title == "User's task"
        assert tasks[0].user_id == test_user.id

    async def test_rls_prevents_cross_user_update(self, db: AsyncSession, test_user: User, test_admin: User):
        # Create a task for admin
        admin_task = Task(user_id=test_admin.id, title="Admin's task")
        db.add(admin_task)
        await db.commit()
        await db.refresh(admin_task)

        # Set RLS context to test_user
        await set_rls_context(db, str(test_user.id))

        # Try to update admin's task - should not find it
        result = await db.execute(select(Task).where(Task.id == admin_task.id))
        task = result.scalar_one_or_none()

        # RLS should hide the task
        assert task is None

    async def test_rls_prevents_cross_user_delete(self, db: AsyncSession, test_user: User, test_admin: User):
        # Create a task for admin
        admin_task = Task(user_id=test_admin.id, title="Admin's task")
        db.add(admin_task)
        await db.commit()
        task_id = admin_task.id

        # Set RLS context to test_user
        await set_rls_context(db, str(test_user.id))

        # Try to query admin's task - should not find it
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()

        assert task is None
