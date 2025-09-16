"""Authentication domain service."""

import re
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password, is_password_strong
from app.domains.auth.exceptions import (
    UserAlreadyExistsError,
    WeakPasswordError, 
    InvalidEmailError
)
from app.infra.models import User


class AuthService:
    """Authentication service for user management."""
    
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def register_user(
        self, 
        email: str, 
        password: str, 
        full_name: str
    ) -> User:
        """
        Register a new user with email, password and full name.
        
        Args:
            email: User's email address
            password: Plain text password
            full_name: User's full name
            
        Returns:
            The created User object
            
        Raises:
            InvalidEmailError: If email format is invalid
            WeakPasswordError: If password doesn't meet requirements
            UserAlreadyExistsError: If user with email already exists
        """
        # Validate email format
        if not self._is_valid_email(email):
            raise InvalidEmailError(email)
        
        # Validate password strength
        is_strong, errors = is_password_strong(password)
        if not is_strong:
            raise WeakPasswordError(errors)
        
        # Check if user already exists
        existing_user = await self._get_user_by_email(email)
        if existing_user:
            raise UserAlreadyExistsError(email)
        
        # Hash the password
        password_hash = hash_password(password)
        
        # Create the user
        user = User(
            email=email.lower().strip(),
            password_hash=password_hash,
            full_name=full_name.strip()
        )
        
        try:
            self.db_session.add(user)
            await self.db_session.commit()
            await self.db_session.refresh(user)
            return user
        except IntegrityError:
            await self.db_session.rollback()
            # This can happen if there's a race condition
            raise UserAlreadyExistsError(email)
    
    async def _get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email address."""
        result = await self.db_session.execute(
            select(User).where(User.email == email.lower().strip())
        )
        return result.scalar_one_or_none()
    
    def _is_valid_email(self, email: str) -> bool:
        """Check if email format is valid."""
        return bool(self.EMAIL_REGEX.match(email.strip()))