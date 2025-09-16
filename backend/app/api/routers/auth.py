"""Authentication API endpoints."""

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.models import (
    UserRegisterRequest, 
    UserResponse, 
    AuthResponse,
    ErrorResponse,
    ValidationErrorResponse
)
from app.domains.auth.service import AuthService
from app.domains.auth.exceptions import (
    UserAlreadyExistsError,
    WeakPasswordError,
    InvalidEmailError
)
from app.infra.db import get_session
from app.core.security import create_access_token

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ValidationErrorResponse, "description": "Validation error"},
        409: {"model": ErrorResponse, "description": "User already exists"},
    },
    summary="Register a new user",
    description="Register a new user with email, password, and full name. "
                "Password must meet security requirements. Returns user info and access token.",
)
async def register_user(
    request: UserRegisterRequest,
    db_session: AsyncSession = Depends(get_session)
) -> AuthResponse:
    """
    Register a new user.
    
    - **email**: Valid email address (will be used for login)
    - **password**: Strong password (min 8 chars, uppercase, lowercase, number, special char)
    - **full_name**: User's full name (2-255 characters)
    
    Returns the created user information (without password).
    """
    logger.info(
        "User registration attempt",
        email=request.email,
        full_name=request.full_name
    )
    
    auth_service = AuthService(db_session)
    
    try:
        user = await auth_service.register_user(
            email=request.email,
            password=request.password,
            full_name=request.full_name
        )
        
        # Create access token for the user
        access_token = create_access_token(user.id, user.email)
        
        logger.info(
            "User registered successfully", 
            user_id=str(user.id),
            email=user.email
        )
        
        return AuthResponse(
            user=UserResponse.model_validate(user),
            access_token=access_token,
            token_type="bearer"
        )
        
    except WeakPasswordError as e:
        logger.warning(
            "User registration failed - weak password",
            email=request.email,
            errors=e.errors
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "detail": "Password validation failed",
                "errors": e.errors
            }
        )
        
    except InvalidEmailError as e:
        logger.warning(
            "User registration failed - invalid email",
            email=request.email
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "detail": str(e),
                "error_type": "InvalidEmailError"
            }
        )
        
    except UserAlreadyExistsError as e:
        logger.warning(
            "User registration failed - user already exists",
            email=request.email
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "detail": str(e),
                "error_type": "UserAlreadyExistsError"
            }
        )
        
    except Exception as e:
        logger.error(
            "User registration failed - unexpected error",
            email=request.email,
            error=str(e),
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration"
        )