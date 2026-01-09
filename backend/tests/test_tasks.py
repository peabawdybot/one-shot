import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.models.user import User
from app.models.task import Task

class TestCreateTask:
    async def test_create_task(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            "/api/tasks",
            json={"title": "My first task", "description": "Task description"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "My first task"
        assert data["description"] == "Task description"
        assert data["is_completed"] is False
        assert "id" in data

    async def test_create_task_empty_title_fails(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            "/api/tasks",
            json={"title": "", "description": "Description"},
            headers=auth_headers,
        )
        assert response.status_code == 422

    async def test_create_task_no_description(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            "/api/tasks",
            json={"title": "Task without description"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["description"] is None

class TestListTasks:
    async def test_list_own_tasks(self, client: AsyncClient, auth_headers: dict, test_user: User, db: AsyncSession):
        # Create tasks for the user
        task1 = Task(user_id=test_user.id, title="Task 1")
        task2 = Task(user_id=test_user.id, title="Task 2")
        db.add_all([task1, task2])
        await db.commit()

        response = await client.get("/api/tasks", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["tasks"]) == 2

    async def test_list_returns_empty_for_new_user(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/tasks", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["tasks"] == []

class TestGetTask:
    async def test_get_single_task(self, client: AsyncClient, auth_headers: dict, test_user: User, db: AsyncSession):
        task = Task(user_id=test_user.id, title="Test Task", description="Description")
        db.add(task)
        await db.commit()
        await db.refresh(task)

        response = await client.get(f"/api/tasks/{task.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["id"] == str(task.id)

    async def test_get_nonexistent_task_returns_404(self, client: AsyncClient, auth_headers: dict):
        response = await client.get(f"/api/tasks/{uuid4()}", headers=auth_headers)
        assert response.status_code == 404

class TestUpdateTask:
    async def test_update_task(self, client: AsyncClient, auth_headers: dict, test_user: User, db: AsyncSession):
        task = Task(user_id=test_user.id, title="Original Title")
        db.add(task)
        await db.commit()
        await db.refresh(task)

        response = await client.put(
            f"/api/tasks/{task.id}",
            json={"title": "Updated Title", "description": "New description"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "New description"

class TestDeleteTask:
    async def test_delete_task(self, client: AsyncClient, auth_headers: dict, test_user: User, db: AsyncSession):
        task = Task(user_id=test_user.id, title="To be deleted")
        db.add(task)
        await db.commit()
        await db.refresh(task)

        response = await client.delete(f"/api/tasks/{task.id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify task is gone
        get_response = await client.get(f"/api/tasks/{task.id}", headers=auth_headers)
        assert get_response.status_code == 404

class TestTaskIsolation:
    async def test_cannot_access_other_user_task(
        self, client: AsyncClient, auth_headers: dict, test_admin: User, db: AsyncSession
    ):
        # Create a task for the admin user
        admin_task = Task(user_id=test_admin.id, title="Admin's private task")
        db.add(admin_task)
        await db.commit()
        await db.refresh(admin_task)

        # Try to access as regular user
        response = await client.get(f"/api/tasks/{admin_task.id}", headers=auth_headers)
        assert response.status_code == 404

    async def test_cannot_update_other_user_task(
        self, client: AsyncClient, auth_headers: dict, test_admin: User, db: AsyncSession
    ):
        admin_task = Task(user_id=test_admin.id, title="Admin's task")
        db.add(admin_task)
        await db.commit()
        await db.refresh(admin_task)

        response = await client.put(
            f"/api/tasks/{admin_task.id}",
            json={"title": "Hacked title"},
            headers=auth_headers,
        )
        assert response.status_code == 404

    async def test_cannot_delete_other_user_task(
        self, client: AsyncClient, auth_headers: dict, test_admin: User, db: AsyncSession
    ):
        admin_task = Task(user_id=test_admin.id, title="Admin's task")
        db.add(admin_task)
        await db.commit()
        await db.refresh(admin_task)

        response = await client.delete(f"/api/tasks/{admin_task.id}", headers=auth_headers)
        assert response.status_code == 404
