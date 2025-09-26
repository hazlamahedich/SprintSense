"""HTTP routes for sprint completion and incomplete items."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.sprint_completion import (
    CompleteSprintRequest,
    CompleteSprintResponse,
    IncompleteTaskDto,
)
from app.services.sprint_completion_service import SprintCompletionService

router = APIRouter(prefix="/api/sprints", tags=["sprints"])


def get_service(db: AsyncSession = Depends(get_db)) -> SprintCompletionService:
    return SprintCompletionService(db)


@router.get("/{sprint_id}/incomplete-items", response_model=List[IncompleteTaskDto])
async def get_incomplete_items(
    sprint_id: UUID,
    db: AsyncSession = Depends(get_db),
    service: SprintCompletionService = Depends(get_service),
    current_user=Depends(get_current_user),
) -> List[IncompleteTaskDto]:
    try:
        return await service.get_incomplete_items(sprint_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/{sprint_id}/complete", response_model=CompleteSprintResponse)
async def complete_sprint(
    sprint_id: UUID,
    payload: CompleteSprintRequest,
    db: AsyncSession = Depends(get_db),
    service: SprintCompletionService = Depends(get_service),
    current_user=Depends(get_current_user),
) -> CompleteSprintResponse:
    try:
        return await service.complete_sprint(
            sprint_id, payload, moved_by=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
