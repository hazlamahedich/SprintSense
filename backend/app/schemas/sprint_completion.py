"""Sprint completion and incomplete work handling DTOs."""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MoveType(str, Enum):
    BACKLOG = "backlog"
    NEXT_SPRINT = "next_sprint"


class SprintCompletionAction(str, Enum):
    """Type of move for incomplete items."""

    BACKLOG = "backlog"
    NEXT_SPRINT = "next_sprint"


class IncompleteWorkResponse(BaseModel):
    """Represents a task that is not complete at sprint end."""

    id: UUID
    title: str
    description: Optional[str] = None
    status: str
    points: int = Field(ge=0)
    assignee_id: Optional[UUID] = None
    assignee_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class MoveToNextSprintRequest(BaseModel):
    """Request to move incomplete items to next sprint."""

    item_ids: List[UUID] = Field(..., description="List of item IDs to move")
    next_sprint_id: UUID = Field(..., description="Target sprint ID")


class MoveToBacklogRequest(BaseModel):
    """Request to move incomplete items to backlog."""

    item_ids: List[UUID] = Field(..., description="List of item IDs to move")


class CompleteSprintRequest(BaseModel):
    """Legacy request used by existing tests to complete sprint."""

    action: MoveType
    item_ids: Optional[List[UUID]] = Field(
        default=None,
        description="Optional list of specific items to move. If not provided, moves all incomplete items.",
    )


class CompleteSprintResponse(BaseModel):
    """Response after completing sprint and moving items."""

    moved_count: int = Field(ge=0)
    target: MoveType
    next_sprint_id: Optional[UUID] = None


# Backward compatibility alias for tests
IncompleteTaskDto = IncompleteWorkResponse


class SprintItemMoveResponse(BaseModel):
    """Record of an item being moved during sprint completion."""

    id: UUID
    task_id: UUID
    from_sprint_id: UUID
    to_sprint_id: Optional[UUID]
    moved_to: MoveType
    moved_by: UUID
    moved_at: datetime
