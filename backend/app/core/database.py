"""Database session management and configuration."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from urllib.parse import urlparse
from app.core.config import settings

# SQLAlchemy engine for async operations
engine = create_async_engine(
    settings.DATABASE_URL, echo=False, future=True, pool_pre_ping=True
)

# Session factory for creating database sessions
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session from the pool."""
    db = SessionLocal()
    try:
        yield db
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    finally:
        await db.close()


def get_db_url() -> str:
    """Get the database URL with sensitive information removed."""
    url = urlparse(str(settings.DATABASE_URL))
    return f"{url.scheme}://{url.hostname}:{url.port}/{url.path.lstrip('/')}"
