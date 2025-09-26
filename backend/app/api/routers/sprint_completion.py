"""Sprint completion router handling incomplete work items when a sprint ends."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.security import get_current_user
from app.schemas.sprint_completion import (
    IncompleteWorkResponse,
    MoveToBacklogRequest,
    MoveToNextSprintRequest,
    SprintCompletionAction,
)
from app.services.sprint_completion_service import SprintCompletionService

router = APIRouter()


@router.get(
    "/sprints/{sprint_id}/incomplete-items", response_model=List[IncompleteWorkResponse]
)
async def get_incomplete_items(
    sprint_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Get incomplete work items for a sprint."""
    service = SprintCompletionService(session)
    return await service.get_incomplete_items(sprint_id)


@router.post("/sprints/{sprint_id}/move-to-backlog")
async def move_to_backlog(
    sprint_id: str,
    request: MoveToBacklogRequest,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Move incomplete work items to the backlog."""
    service = SprintCompletionService(session)
    await service.move_to_backlog(sprint_id, request.item_ids, current_user["id"])
    return {"status": "success", "action": SprintCompletionAction.MOVE_TO_BACKLOG}


@router.post("/sprints/{sprint_id}/move-to-next-sprint")
async def move_to_next_sprint(
    sprint_id: str,
    request: MoveToNextSprintRequest,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Move incomplete work items to the next sprint."""
    service = SprintCompletionService(session)
    await service.move_to_next_sprint(
        sprint_id, request.item_ids, request.next_sprint_id, current_user["id"]
    )
    return {"status": "success", "action": SprintCompletionAction.MOVE_TO_NEXT_SPRINT}
