"""Authentication endpoints for user login and logout."""

from datetime import timedelta
from typing import Any, Dict

import structlog
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token
from app.domains.schemas.user import UserLoginRequest, UserResponse
from app.domains.services.user_service import UserService
from app.infra.db import get_session

logger = structlog.get_logger(__name__)

router = APIRouter()
security = HTTPBearer()


async def get_user_service(db: AsyncSession = Depends(get_session)) -> UserService:
    """Dependency to get user service with database session."""
    return UserService(db)


@router.post(
    "/login",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate user with email and password, return secure cookie",
)
async def login_user(
    response: Response,
    user_data: UserLoginRequest,
    user_service: UserService = Depends(get_user_service),
) -> Dict[str, Any]:
    """Authenticate user and set secure session cookie.

    Args:
        response: FastAPI response object for setting cookies
        user_data: User login credentials
        user_service: User service dependency

    Returns:
        Dict containing user data and success message

    Raises:
        HTTPException: 401 for invalid credentials, 400 for validation errors
    """
    logger.info("User login attempt", email=user_data.email)

    try:
        # Authenticate the user
        user = await user_service.authenticate_user(
            email=user_data.email, password=user_data.password
        )

        if not user:
            logger.warning("Login failed - invalid credentials", email=user_data.email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            logger.warning("Login failed - inactive user", email=user_data.email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive",
            )

        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires,
        )

        # Set secure HTTP-only cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
            httponly=True,  # Prevent XSS attacks
            secure=settings.ENVIRONMENT == "production",  # HTTPS only in production
            samesite="strict",  # CSRF protection
            path="/",  # Cookie available for entire site
        )

        logger.info("User login successful", user_id=str(user.id), email=user.email)

        return {
            "message": "Login successful",
            "user": UserResponse.model_validate(user).model_dump(),
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        logger.error("Login failed - unexpected error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login",
        )


@router.post(
    "/logout",
    response_model=Dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="User logout",
    description="Clear user session and remove authentication cookie",
)
async def logout_user(response: Response) -> Dict[str, str]:
    """Logout user by clearing session cookie.

    Args:
        response: FastAPI response object for clearing cookies

    Returns:
        Dict containing success message
    """
    logger.info("User logout")

    try:
        # Clear the authentication cookie
        response.delete_cookie(
            key="access_token",
            path="/",
            httponly=True,
            secure=settings.ENVIRONMENT == "production",
            samesite="strict",
        )

        logger.info("User logout successful")

        return {"message": "Logout successful"}

    except Exception as e:
        logger.error("Logout failed - unexpected error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during logout",
        )
