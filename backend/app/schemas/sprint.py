"""Sprint schemas."""

from datetime import date, datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class SprintStatus(str, Enum):
    """Sprint status enum."""

    FUTURE = "future"
    ACTIVE = "active"
    CLOSED = "closed"


class SprintBase(BaseModel):
    """Shared sprint fields."""

    name: str = Field(..., min_length=1, max_length=255)
    goal: Optional[str] = None


class SprintCreate(SprintBase):
    """Sprint creation schema."""

    start_date: date = Field(...)
    end_date: date = Field(...)

    @model_validator(mode="after")
    def validate_dates(self) -> "SprintCreate":
        """Validate that end_date is after start_date."""
        if self.start_date >= self.end_date:
            raise ValueError("end_date must be after start_date")
        return self


class SprintUpdate(BaseModel):
    """Sprint update schema."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    goal: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    @model_validator(mode="after")
    def validate_dates(self) -> "SprintUpdate":
        """Validate that end_date is after start_date if both are provided."""
        if self.start_date is not None and self.end_date is not None:
            if self.start_date >= self.end_date:
                raise ValueError("end_date must be after start_date")
        return self


class SprintStatusUpdate(BaseModel):
    """Sprint status update schema."""

    status: SprintStatus = Field(
        ...,
        description="New sprint status. Valid transitions are:\n"
        "- future -> active\n"
        "- active -> closed",
    )


class SprintResponse(SprintBase):
    """Sprint response schema."""

    id: UUID
    team_id: UUID
    status: SprintStatus
    start_date: date
    end_date: date
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True
