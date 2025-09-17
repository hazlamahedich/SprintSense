"""WorkItem Pydantic schemas for request/response validation."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.domains.models.work_item import WorkItemStatus, WorkItemType


class WorkItemBase(BaseModel):
    """Base work item schema with shared properties."""

    title: str
    description: Optional[str] = None
    type: WorkItemType = WorkItemType.STORY
    priority: float = 0.0
    story_points: Optional[int] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is not empty."""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        if len(v.strip()) > 255:
            raise ValueError("Title cannot exceed 255 characters")
        return v.strip()

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: float) -> float:
        """Validate priority is non-negative."""
        if v < 0:
            raise ValueError("Priority cannot be negative")
        return v

    @field_validator("story_points")
    @classmethod
    def validate_story_points(cls, v: Optional[int]) -> Optional[int]:
        """Validate story points if provided."""
        if v is not None and v < 0:
            raise ValueError("Story points cannot be negative")
        return v


class WorkItemCreateRequest(WorkItemBase):
    """Schema for work item creation request."""

    team_id: uuid.UUID
    assignee_id: Optional[uuid.UUID] = None


class WorkItemUpdateRequest(BaseModel):
    """Schema for work item update request."""

    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[WorkItemType] = None
    status: Optional[WorkItemStatus] = None
    priority: Optional[float] = None
    story_points: Optional[int] = None
    assignee_id: Optional[uuid.UUID] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate title if provided."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Title cannot be empty")
            if len(v.strip()) > 255:
                raise ValueError("Title cannot exceed 255 characters")
            return v.strip()
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: Optional[float]) -> Optional[float]:
        """Validate priority if provided."""
        if v is not None and v < 0:
            raise ValueError("Priority cannot be negative")
        return v

    @field_validator("story_points")
    @classmethod
    def validate_story_points(cls, v: Optional[int]) -> Optional[int]:
        """Validate story points if provided."""
        if v is not None and v < 0:
            raise ValueError("Story points cannot be negative")
        return v


class WorkItemResponse(WorkItemBase):
    """Schema for work item response."""

    id: uuid.UUID
    team_id: uuid.UUID
    sprint_id: Optional[uuid.UUID] = None
    author_id: uuid.UUID
    assignee_id: Optional[uuid.UUID] = None
    status: WorkItemStatus
    completed_at: Optional[datetime] = None
    source_sprint_id_for_action_item: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class WorkItemListResponse(BaseModel):
    """Schema for work item list response."""

    items: list[WorkItemResponse]
    total: int
    page: int
    size: int

    model_config = ConfigDict(from_attributes=True)
