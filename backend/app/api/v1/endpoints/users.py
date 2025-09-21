"""User endpoints for registration and user management."""

from typing import Any, Dict

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.domains.schemas.user import UserCreateRequest, UserResponse
from app.domains.services.user_service import UserService
from app.infra.db import get_session

logger = structlog.get_logger(__name__)

router = APIRouter()


async def get_user_service(db: AsyncSession = Depends(get_session)) -> UserService:
    """Dependency to get user service with database session."""
    return UserService(db)


@router.post(
    "/register",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account and return access token",
)
async def register_user(
    user_data: UserCreateRequest,
    user_service: UserService = Depends(get_user_service),
) -> Dict[str, Any]:
    """Register a new user account.

    Args:
        user_data: User registration data
        user_service: User service dependency

    Returns:
        Dict containing user data and access token

    Raises:
        HTTPException: 409 if email already exists, 400 for validation errors
    """
    logger.info("User registration attempt", email=user_data.email)

    try:
        # Create the user
        user = await user_service.create_user(user_data)

        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )

        logger.info(
            "User registration successful", user_id=str(user.id), email=user.email
        )

        return {
            "message": "User registered successfully",
            "user": UserResponse.model_validate(user).model_dump(),
            "access_token": access_token,
            "token_type": "bearer",
        }

    except ValueError as e:
        if "Email already registered" in str(e):
            logger.warning(
                "Registration failed - email already exists", email=user_data.email
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email address is already registered",
            )

        logger.warning("Registration failed - validation error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception as e:
        logger.error("Registration failed - unexpected error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration",
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Get the profile of the currently authenticated user",
)
async def get_current_user_profile(
    # TODO: Add authentication dependency when auth is implemented
    # current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Get current user profile (placeholder for future authentication)."""
    # This is a placeholder endpoint for future authentication implementation
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication not yet implemented",
    )

