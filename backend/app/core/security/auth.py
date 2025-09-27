"""User authentication dependencies."""

from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.core.security.tokens import verify_token
from app.core.logging import logger
from app.domains.models.user import User
from app.domains.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    """Get current authenticated user.

    Args:
        token: JWT bearer token

    Returns:
        User: Current user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        payload = verify_token(token)
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate token",
                headers={"WWW-Authenticate": "Bearer"}
            )

        user_service = UserService()
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

async def get_current_active_user(
    user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Get current active user.

    Args:
        user: Current authenticated user

    Returns:
        User: Current active user

    Raises:
        HTTPException: If user is inactive
    """
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return user