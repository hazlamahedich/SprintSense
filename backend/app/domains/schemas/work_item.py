"""WorkItem Pydantic schemas for request/response validation."""

import uuid
from datetime import datetime
from enum import Enum
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


class WorkItemCreateRequest(BaseModel):
    """Schema for work item creation request."""

    team_id: uuid.UUID
    title: str
    description: Optional[str] = None
    type: WorkItemType = WorkItemType.STORY
    priority: Optional[float] = None  # If provided, used; otherwise auto-calculated
    story_points: Optional[int] = None
    assignee_id: Optional[uuid.UUID] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title meets requirements."""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        if len(v.strip()) > 200:  # Match story requirements
            raise ValueError("Title cannot exceed 200 characters")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate description meets requirements."""
        if v is not None:
            if len(v.strip()) > 2000:  # Match story requirements
                raise ValueError("Description cannot exceed 2000 characters")
            return v.strip() if v.strip() else None
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


class PriorityAction(str, Enum):
    """Enum for priority change actions."""

    MOVE_TO_TOP = "move_to_top"
    MOVE_UP = "move_up"
    MOVE_DOWN = "move_down"
    MOVE_TO_BOTTOM = "move_to_bottom"
    SET_POSITION = "set_position"


class PriorityUpdateRequest(BaseModel):
    """Schema for work item priority update request."""

    action: PriorityAction
    position: Optional[int] = None  # Used with SET_POSITION action

    @field_validator("position")
    @classmethod
    def validate_position(cls, v: Optional[int], info) -> Optional[int]:
        """Validate position when action is SET_POSITION."""
        if info.data.get("action") == PriorityAction.SET_POSITION:
            if v is None:
                raise ValueError("Position is required for SET_POSITION action")
            if v < 1:
                raise ValueError("Position must be positive (1-based index)")
        return v
