import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.models.task import Task

class TestAdminListUsers:
    async def test_admin_list_users(self, client: AsyncClient, admin_headers: dict, test_user: User):
        response = await client.get("/api/admin/users", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert data["total"] >= 1

    async def test_non_admin_forbidden(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/admin/users", headers=auth_headers)
        assert response.status_code == 403

class TestAdminGetUser:
    async def test_admin_get_user_details(
        self, client: AsyncClient, admin_headers: dict, test_user: User, db: AsyncSession
    ):
        # Add some tasks for the user
        task1 = Task(user_id=test_user.id, title="Task 1")
        task2 = Task(user_id=test_user.id, title="Task 2")
        db.add_all([task1, task2])
        await db.commit()

        response = await client.get(f"/api/admin/users/{test_user.id}", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["task_count"] == 2

    async def test_admin_get_nonexistent_user(self, client: AsyncClient, admin_headers: dict):
        from uuid import uuid4
        response = await client.get(f"/api/admin/users/{uuid4()}", headers=admin_headers)
        assert response.status_code == 404

class TestAdminUpdateUser:
    async def test_admin_deactivate_user(
        self, client: AsyncClient, admin_headers: dict, test_user: User
    ):
        response = await client.patch(
            f"/api/admin/users/{test_user.id}",
            json={"is_active": False},
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False

    async def test_admin_reactivate_user(
        self, client: AsyncClient, admin_headers: dict, test_user: User, db: AsyncSession
    ):
        # First deactivate
        test_user.is_active = False
        await db.commit()

        # Then reactivate
        response = await client.patch(
            f"/api/admin/users/{test_user.id}",
            json={"is_active": True},
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is True

    async def test_admin_cannot_deactivate_self(
        self, client: AsyncClient, admin_headers: dict, test_admin: User
    ):
        response = await client.patch(
            f"/api/admin/users/{test_admin.id}",
            json={"is_active": False},
            headers=admin_headers,
        )
        assert response.status_code == 400
        assert "own account" in response.json()["detail"].lower()

class TestNonAdminAccess:
    async def test_non_admin_cannot_list_users(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/admin/users", headers=auth_headers)
        assert response.status_code == 403

    async def test_non_admin_cannot_get_user(
        self, client: AsyncClient, auth_headers: dict, test_admin: User
    ):
        response = await client.get(f"/api/admin/users/{test_admin.id}", headers=auth_headers)
        assert response.status_code == 403

    async def test_non_admin_cannot_update_user(
        self, client: AsyncClient, auth_headers: dict, test_admin: User
    ):
        response = await client.patch(
            f"/api/admin/users/{test_admin.id}",
            json={"is_active": False},
            headers=auth_headers,
        )
        assert response.status_code == 403
