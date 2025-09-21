"""ProjectGoal Pydantic schemas for request/response validation."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class ProjectGoalBase(BaseModel):
    """Base project goal schema with shared properties."""

    description: str
    priority_weight: int
    success_metrics: Optional[str] = None

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate goal description meets requirements."""
        if not v or not v.strip():
            raise ValueError("Goal description cannot be empty")
        if len(v.strip()) > 500:  # Match AC3 requirements
            raise ValueError("Goal description cannot exceed 500 characters")
        return v.strip()

    @field_validator("priority_weight")
    @classmethod
    def validate_priority_weight(cls, v: int) -> int:
        """Validate priority weight is within allowed range."""
        if v < 1 or v > 10:  # Match AC3 requirements
            raise ValueError("Priority weight must be between 1 and 10")
        return v

    @field_validator("success_metrics")
    @classmethod
    def validate_success_metrics(cls, v: Optional[str]) -> Optional[str]:
        """Validate success metrics if provided."""
        if v is not None:
            if len(v.strip()) > 1000:  # Reasonable limit for success metrics
                raise ValueError("Success metrics cannot exceed 1000 characters")
            return v.strip() if v.strip() else None
        return v


class ProjectGoalCreateRequest(ProjectGoalBase):
    """Schema for project goal creation request."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "description": "Improve user engagement by 25% through better navigation",
                    "priority_weight": 8,
                    "success_metrics": "Monthly active users increase by 25%, session duration increases by 15%",
                },
                {
                    "description": "Reduce customer support tickets by implementing self-service features",
                    "priority_weight": 7,
                    "success_metrics": "Support ticket volume decreases by 30% within 3 months",
                },
                {
                    "description": "Enhance system performance and reliability",
                    "priority_weight": 9,
                    "success_metrics": "Page load times under 2 seconds, 99.9% uptime",
                },
            ]
        }
    )


class ProjectGoalUpdateRequest(BaseModel):
    """Schema for project goal update request."""

    description: Optional[str] = None
    priority_weight: Optional[int] = None
    success_metrics: Optional[str] = None

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate goal description if provided."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Goal description cannot be empty")
            if len(v.strip()) > 500:
                raise ValueError("Goal description cannot exceed 500 characters")
            return v.strip()
        return v

    @field_validator("priority_weight")
    @classmethod
    def validate_priority_weight(cls, v: Optional[int]) -> Optional[int]:
        """Validate priority weight if provided."""
        if v is not None:
            if v < 1 or v > 10:
                raise ValueError("Priority weight must be between 1 and 10")
        return v

    @field_validator("success_metrics")
    @classmethod
    def validate_success_metrics(cls, v: Optional[str]) -> Optional[str]:
        """Validate success metrics if provided."""
        if v is not None:
            if len(v.strip()) > 1000:
                raise ValueError("Success metrics cannot exceed 1000 characters")
            return v.strip() if v.strip() else None
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "description": "Updated goal description with clearer success criteria",
                    "priority_weight": 9,
                },
                {
                    "priority_weight": 5,
                    "success_metrics": "New success metrics after goal refinement",
                },
            ]
        }
    )


class ProjectGoalResponse(ProjectGoalBase):
    """Schema for project goal response."""

    id: uuid.UUID
    team_id: uuid.UUID
    author_id: uuid.UUID
    created_by: uuid.UUID
    updated_by: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "team_id": "223e4567-e89b-12d3-a456-426614174001",
                    "description": "Improve user engagement by 25% through better navigation",
                    "priority_weight": 8,
                    "success_metrics": "Monthly active users increase by 25%, session duration increases by 15%",
                    "author_id": "323e4567-e89b-12d3-a456-426614174002",
                    "created_by": "323e4567-e89b-12d3-a456-426614174002",
                    "updated_by": None,
                    "created_at": "2025-01-19T12:30:00Z",
                    "updated_at": None,
                }
            ]
        },
    )


class ProjectGoalListResponse(BaseModel):
    """Schema for project goal list response."""

    goals: list[ProjectGoalResponse]
    total: int

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "goals": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "team_id": "223e4567-e89b-12d3-a456-426614174001",
                            "description": "Improve user engagement by 25%",
                            "priority_weight": 8,
                            "success_metrics": "MAU increase by 25%",
                            "author_id": "323e4567-e89b-12d3-a456-426614174002",
                            "created_by": "323e4567-e89b-12d3-a456-426614174002",
                            "updated_by": None,
                            "created_at": "2025-01-19T12:30:00Z",
                            "updated_at": None,
                        }
                    ],
                    "total": 1,
                }
            ]
        },
    )


class ProjectGoalUniqueValidationError(BaseModel):
    """Schema for goal uniqueness validation error response."""

    error_code: str = "DUPLICATE_GOAL"
    message: str = "A goal with this description already exists for this team"
    existing_goal_id: uuid.UUID
    recovery_action: str = (
        "Please modify the goal description or update the existing goal"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "error_code": "DUPLICATE_GOAL",
                    "message": "A goal with this description already exists for this team",
                    "existing_goal_id": "123e4567-e89b-12d3-a456-426614174000",
                    "recovery_action": "Please modify the goal description or update the existing goal",
                }
            ]
        }
    )

