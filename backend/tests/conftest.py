"""Test configuration and fixtures."""

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.infra.db import Base, get_session
from app.main import app

# Test database URL (using SQLite for simplicity in tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
)

# Create test session factory
TestSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_test_session():
    """Get test database session."""
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def db_session():
    """Create test database session with clean setup."""
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async with TestSessionLocal() as session:
        yield session

    # Clean up - drop all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession):
    """Create test client with database dependency override."""

    # Override the dependency to use our test session
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    # Clean up
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session):
    """Create a test user in the database."""
    from app.domains.services.user_service import UserService
    from app.domains.schemas.user import UserCreate
    
    user_service = UserService(db_session)
    user_data = UserCreate(
        email="testuser@example.com",
        full_name="Test User", 
        password="TestPassword123"
    )
    
    user = await user_service.create_user(user_data)
    return user


@pytest_asyncio.fixture
async def auth_headers_for_user(test_user):
    """Create authentication headers for the test user."""
    from app.core.security import create_access_token
    from datetime import timedelta
    
    access_token = create_access_token(
        data={"sub": str(test_user.id), "email": test_user.email},
        expires_delta=timedelta(minutes=30)
    )
    
    return {"Cookie": f"access_token={access_token}"}
