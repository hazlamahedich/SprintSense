"""Seed script to create test user."""

import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.security import get_password_hash
from app.domains.models.user import User


async def create_test_users(session: AsyncSession) -> None:
    """Create test users if they don't exist."""
    # Test users data
    users = [
        {
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "TestPass123",
        },
        {
            "email": "other@example.com",
            "full_name": "Other Test User",
            "password": "TestPass123",
        },
    ]

    for user_data in users:
        # Check if user exists
        query = text("SELECT id FROM users WHERE email = :email")
        result = await session.execute(query, {"email": user_data["email"]})
        existing_user = result.scalar()

        if not existing_user:
            # Create user
            user = User(
                email=user_data["email"],
                full_name=user_data["full_name"],
                hashed_password=get_password_hash(user_data["password"]),
                is_active=True,
            )
            session.add(user)
            await session.commit()
            print(f"Created user: {user_data['email']}")
        else:
            print(f"User already exists: {user_data['email']}")


async def main() -> None:
    """Main function to run seed script."""
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        await create_test_users(session)


if __name__ == "__main__":
    asyncio.run(main())
