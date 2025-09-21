"""Authentication dependencies and utilities."""

import uuid
from typing import Optional

import structlog
from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_token
from app.domains.models.user import User
from app.domains.services.user_service import UserService
from app.infra.db import get_session

logger = structlog.get_logger(__name__)


async def get_user_service(db: AsyncSession = Depends(get_session)) -> UserService:
    """Dependency to get user service with database session."""
    return UserService(db)


async def get_current_user(
    access_token: Optional[str] = Cookie(None),
    user_service: UserService = Depends(get_user_service),
) -> User:
    """Get the current authenticated user from the access token cookie.

    Args:
        access_token: JWT token from HTTP-only cookie
        user_service: User service dependency

    Returns:
        User: The authenticated user

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not access_token:
        logger.warning("No access token provided")
        raise credentials_exception

    # Verify token
    payload = verify_token(access_token)
    if not payload:
        logger.warning("Invalid access token")
        raise credentials_exception

    # Get user ID from token
    user_id_str: Optional[str] = payload.get("sub")
    if not user_id_str:
        logger.warning("No user ID in token")
        raise credentials_exception

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        logger.warning("Invalid user ID format", user_id=user_id_str)
        raise credentials_exception

    # Get user from database
    user = await user_service.get_user_by_id(str(user_id))
    if not user:
        logger.warning("User not found", user_id=user_id_str)
        raise credentials_exception

    if not user.is_active:
        logger.warning("User is inactive", user_id=user_id_str)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )

    logger.info("User authenticated successfully", user_id=user_id_str)
    return user

