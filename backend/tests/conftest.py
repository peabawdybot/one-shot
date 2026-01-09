import asyncio
from typing import AsyncGenerator
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.database import Base, get_db
from app.main import app
from app.models import User, Task, RefreshToken
from app.services.auth import hash_password, create_access_token
from app.models.user import UserRole

TEST_DATABASE_URL = "postgresql+asyncpg://taskmanager:changeme@localhost:5432/taskmanager_test"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
)

test_session_maker = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with test_session_maker() as session:
        yield session

@pytest.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()

@pytest.fixture
async def test_user(db: AsyncSession) -> User:
    user = User(
        email="test@example.com",
        password_hash=hash_password("testpassword123"),
        role=UserRole.USER,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@pytest.fixture
async def test_admin(db: AsyncSession) -> User:
    user = User(
        email="admin@example.com",
        password_hash=hash_password("adminpassword123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@pytest.fixture
def user_token(test_user: User) -> str:
    return create_access_token({"sub": str(test_user.id), "email": test_user.email, "role": test_user.role.value})

@pytest.fixture
def admin_token(test_admin: User) -> str:
    return create_access_token({"sub": str(test_admin.id), "email": test_admin.email, "role": test_admin.role.value})

@pytest.fixture
def auth_headers(user_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {user_token}"}

@pytest.fixture
def admin_headers(admin_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {admin_token}"}
