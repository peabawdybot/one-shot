import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.services.auth import hash_password

class TestRegister:
    async def test_register_success(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/register",
            json={"email": "newuser@example.com", "password": "securepassword123"},
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["role"] == "user"

    async def test_register_duplicate_email(self, client: AsyncClient, test_user: User):
        response = await client.post(
            "/api/auth/register",
            json={"email": test_user.email, "password": "anotherpassword123"},
        )
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"].lower()

    async def test_register_invalid_email(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/register",
            json={"email": "not-an-email", "password": "securepassword123"},
        )
        assert response.status_code == 422

    async def test_register_weak_password(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/register",
            json={"email": "user@example.com", "password": "short"},
        )
        assert response.status_code == 422

class TestLogin:
    async def test_login_success(self, client: AsyncClient, test_user: User):
        response = await client.post(
            "/api/auth/login",
            json={"email": test_user.email, "password": "testpassword123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == test_user.email

    async def test_login_invalid_credentials(self, client: AsyncClient, test_user: User):
        response = await client.post(
            "/api/auth/login",
            json={"email": test_user.email, "password": "wrongpassword"},
        )
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    async def test_login_nonexistent_user(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/login",
            json={"email": "nonexistent@example.com", "password": "anypassword123"},
        )
        assert response.status_code == 401

    async def test_login_deactivated_user(self, client: AsyncClient, db: AsyncSession):
        user = User(
            email="deactivated@example.com",
            password_hash=hash_password("password123"),
            role=UserRole.USER,
            is_active=False,
        )
        db.add(user)
        await db.commit()

        response = await client.post(
            "/api/auth/login",
            json={"email": "deactivated@example.com", "password": "password123"},
        )
        assert response.status_code == 403
        assert "deactivated" in response.json()["detail"].lower()

class TestLogout:
    async def test_logout_clears_session(self, client: AsyncClient, auth_headers: dict):
        response = await client.post("/api/auth/logout", headers=auth_headers)
        assert response.status_code == 204

class TestProtectedRoutes:
    async def test_protected_route_requires_auth(self, client: AsyncClient):
        response = await client.get("/api/auth/me")
        assert response.status_code == 403  # No auth header

    async def test_me_returns_current_user(self, client: AsyncClient, auth_headers: dict, test_user: User):
        response = await client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["id"] == str(test_user.id)
