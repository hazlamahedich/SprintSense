from typing import Optional
from uuid import UUID

from databases import Database
from fastapi import APIRouter, Depends, HTTPException

from ..dependencies.auth import get_current_user
from ..dependencies.database import get_db
from ..models.user import User
from ..services.sprint_assignment_service import (
    SprintAssignmentService,
    WorkItemSprintAssignment,
)

router = APIRouter()


@router.patch(
    "/work-items/{work_item_id}/sprint", response_model=WorkItemSprintAssignment
)
async def assign_work_item_to_sprint(
    work_item_id: UUID,
    sprint_id: Optional[UUID] = None,
    current_version: int = None,
    db: Database = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Assign a work item to a sprint or remove it from a sprint.
    Requires:
    - work_item_id: UUID of the work item
    - sprint_id: Optional UUID of the sprint to assign to (null to remove)
    - current_version: Current version of the work item for optimistic locking
    """
    if current_version is None:
        raise HTTPException(status_code=400, detail="current_version is required")

    service = SprintAssignmentService(db)
    return await service.assign_work_item_to_sprint(
        work_item_id=work_item_id,
        sprint_id=sprint_id,
        current_version=current_version,
        user_id=current_user.id,
    )
