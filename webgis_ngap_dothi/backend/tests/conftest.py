"""
tests/conftest.py - Fixture dùng chung cho toàn bộ test suite
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.repositories.db_connection import Base, get_db

# DB test riêng (SQLite in-memory, không dùng PostGIS)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """Tạo bảng test trước khi chạy, xóa sau khi xong"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    """Session DB sạch cho mỗi test"""
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    """HTTP test client với DB được inject"""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_token(client: AsyncClient):
    """Token Admin để test các route yêu cầu quyền Admin"""
    resp = await client.post("/api/auth/login", data={
        "username": "admin", "password": "admin123"
    })
    return resp.json().get("access_token", "")


@pytest_asyncio.fixture
async def user_token(client: AsyncClient):
    """Token User thường"""
    # Đăng ký trước
    await client.post("/api/auth/register", json={
        "username": "testuser", "email": "test@test.com", "password": "test123"
    })
    resp = await client.post("/api/auth/login", data={
        "username": "testuser", "password": "test123"
    })
    return resp.json().get("access_token", "")

