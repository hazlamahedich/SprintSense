"""Pydantic models for API request/response validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Request model for user registration."""
    
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=100,
        description="User's password (8-100 characters)"
    )
    full_name: str = Field(
        ..., 
        min_length=2, 
        max_length=255,
        description="User's full name"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "password": "SecurePass123!",
                "full_name": "John Doe"
            }
        }


class UserResponse(BaseModel):
    """Response model for user data."""
    
    id: UUID = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    full_name: str = Field(..., description="User's full name")
    created_at: datetime = Field(..., description="When the user was created")
    updated_at: datetime = Field(..., description="When the user was last updated")
    
    class Config:
        from_attributes = True  # Enable ORM mode for SQLAlchemy models
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "john.doe@example.com", 
                "full_name": "John Doe",
                "created_at": "2025-09-15T12:00:00Z",
                "updated_at": "2025-09-15T12:00:00Z"
            }
        }


class AuthResponse(BaseModel):
    """Response model for authentication (registration/login)."""
    
    user: UserResponse = Field(..., description="User information")
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "john.doe@example.com",
                    "full_name": "John Doe",
                    "created_at": "2025-09-15T12:00:00Z",
                    "updated_at": "2025-09-15T12:00:00Z"
                },
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class ErrorResponse(BaseModel):
    """Response model for API errors."""
    
    detail: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Type of error")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "User with email 'john@example.com' already exists",
                "error_type": "UserAlreadyExistsError"
            }
        }


class ValidationErrorResponse(BaseModel):
    """Response model for validation errors."""
    
    detail: str = Field(..., description="Error message")
    errors: list[str] = Field(..., description="List of validation errors")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Password validation failed",
                "errors": [
                    "Password must be at least 8 characters long",
                    "Password must contain at least one uppercase letter"
                ]
            }
        }