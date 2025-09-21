"""Test configuration and fixtures."""

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.infra.db import Base, get_session
from app.main import app as fastapi_app

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
async def app():
    """Provide FastAPI app for tests."""
    return fastapi_app


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession, app):
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
async def authenticated_async_client(db_session: AsyncSession, authenticated_user):
    """Create authenticated test client for invitation tests."""
    from datetime import timedelta

    from app.core.security import create_access_token

    # Create access token for authenticated user
    access_token = create_access_token(
        data={"sub": str(authenticated_user.id), "email": authenticated_user.email},
        expires_delta=timedelta(minutes=30),
    )

    # Override the dependency to use our test session
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        app=app, base_url="http://test", cookies={"access_token": access_token}
    ) as ac:
        yield ac

    # Clean up
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session):
    """Create a test user in the database."""
    from app.domains.schemas.user import UserCreate
    from app.domains.services.user_service import UserService

    user_service = UserService(db_session)
    user_data = UserCreate(
        email="testuser@example.com", full_name="Test User", password="TestPassword123"
    )

    user = await user_service.create_user(user_data)
    return user


@pytest_asyncio.fixture
async def auth_headers_for_user(test_user):
    """Create authentication headers for the test user."""
    from datetime import timedelta

    from app.core.security import create_access_token

    access_token = create_access_token(
        data={"sub": str(test_user.id), "email": test_user.email},
        expires_delta=timedelta(minutes=30),
    )

    return {"Cookie": f"access_token={access_token}"}


@pytest_asyncio.fixture
async def authenticated_user(db_session):
    """Create an authenticated user for invitation tests."""
    from app.domains.schemas.user import UserCreate
    from app.domains.services.user_service import UserService

    user_service = UserService(db_session)
    user_data = UserCreate(
        email="owner@example.com", full_name="Team Owner", password="TestPassword123"
    )

    user = await user_service.create_user(user_data)
    return user


@pytest_asyncio.fixture
async def other_user(db_session):
    """Create another user for invitation tests."""
    from app.domains.schemas.user import UserCreate
    from app.domains.services.user_service import UserService

    user_service = UserService(db_session)
    user_data = UserCreate(
        email="member@example.com", full_name="Team Member", password="TestPassword123"
    )

    user = await user_service.create_user(user_data)
    return user


@pytest_asyncio.fixture
async def user_team(db_session, authenticated_user):
    """Create a team owned by the authenticated user."""
    from app.domains.schemas.team import TeamCreateRequest
    from app.domains.services.team_service import TeamService

    team_service = TeamService(db_session)
    team_data = TeamCreateRequest(name="Test Team")

    team = await team_service.create_team(team_data, authenticated_user)
    return team
