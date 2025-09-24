"""Pydantic schemas for project goals."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectGoalBase(BaseModel):
    """Base project goal schema."""

    description: str = Field(..., min_length=1, max_length=500)
    priority_weight: int = Field(..., ge=1, le=10)
    success_metrics: Optional[str] = Field(None, max_length=500)


class ProjectGoalCreate(ProjectGoalBase):
    """Project goal creation schema."""

    pass


class ProjectGoalRead(ProjectGoalBase):
    """Project goal read schema."""

    id: UUID
    team_id: UUID
    author_id: UUID
    created_at: datetime
    created_by: UUID

    class Config:
        """Pydantic config."""

        from_attributes = True


class ProjectGoalList(BaseModel):
    """Project goals list schema."""

    goals: List[ProjectGoalRead]
    total: int
