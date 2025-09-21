"""Test database session management."""

from typing import AsyncGenerator
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.database import Base, get_db

# Test database URL (using PostgreSQL for test to match production)
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/sprintsense_test"

@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Get test database session."""
    TestingSessionLocal = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture
async def get_test_db(test_session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    """Override database dependency for tests."""
    async def _get_test_db():
        yield test_session
    return _get_test_db
