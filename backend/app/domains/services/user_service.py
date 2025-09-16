"""User service with business logic for user registration and management."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.domains.models.user import User
from app.domains.schemas.user import UserCreate, UserCreateRequest, UserRead


class UserService:
    """Service class for user-related business logic."""

    def __init__(self, db_session: AsyncSession) -> None:
        """Initialize the user service with a database session."""
        self.db_session = db_session

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        result = await self.db_session.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        result = await self.db_session.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def create_user(self, user_data: UserCreateRequest) -> UserRead:
        """Create a new user account.

        Args:
            user_data: User registration data

        Returns:
            UserRead: The created user data

        Raises:
            ValueError: If email already exists
        """
        # Check if user with this email already exists
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("Email already registered")

        # Hash the password
        hashed_password = get_password_hash(user_data.password)

        # Create new user instance
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=True,
        )

        # Add to database
        self.db_session.add(user)
        await self.db_session.commit()
        await self.db_session.refresh(user)

        # Return user data (excluding password)
        return UserRead.model_validate(user)

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = await self.get_user_by_email(email)
        if not user:
            return None

        from app.core.security import verify_password

        if not verify_password(password, user.hashed_password):
            return None

        return user

    async def is_email_taken(self, email: str) -> bool:
        """Check if email address is already taken."""
        user = await self.get_user_by_email(email)
        return user is not None
