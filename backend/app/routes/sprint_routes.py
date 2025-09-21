"""Sprint API endpoints."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.domains.models.team import Team
from app.domains.models.user import User
from app.schemas.sprint import SprintCreate, SprintResponse, SprintStatusUpdate
from app.services.sprint_service import SprintService

router = APIRouter(tags=["sprints"])


async def get_sprint_service() -> SprintService:
    """Get sprint service instance."""
    return SprintService()


async def verify_team_access(team_id: UUID, user: User, session: AsyncSession) -> Team:
    """Verify user has access to team and return team if exists."""
    from sqlalchemy import select

    query = (
        select(Team)
        .join(Team.members)
        .where(Team.id == team_id, Team.members.user_id == user.id)
    )
    result = await session.execute(query)
    team = result.scalar_one_or_none()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found or access denied",
        )
    return team


@router.post(
    "/teams/{team_id}/sprints",
    response_model=SprintResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_sprint(
    team_id: UUID,
    sprint_data: SprintCreate,
    current_user: User = Depends(get_current_user),
    service: SprintService = Depends(get_sprint_service),
    session: AsyncSession = Depends(get_db),
) -> SprintResponse:
    """
    Create a new sprint.

    Parameters:
        team_id: Team ID to create the sprint for
        sprint_data: Sprint creation data
        current_user: Current authenticated user
        service: Sprint service instance
        session: Database session

    Returns:
        Created sprint details
    """
    # Verify team access
    await verify_team_access(team_id, current_user, session)

    sprint = await service.create_sprint(session, team_id, sprint_data)
    return SprintResponse.model_validate(sprint)


@router.patch("/sprints/{sprint_id}", response_model=SprintResponse)
async def update_sprint_status(
    sprint_id: UUID,
    status_update: SprintStatusUpdate,
    current_user: User = Depends(get_current_user),
    service: SprintService = Depends(get_sprint_service),
    session: AsyncSession = Depends(get_db),
) -> SprintResponse:
    """
    Update a sprint's status.

    Parameters:
        sprint_id: Sprint ID to update
        status_update: New status data
        current_user: Current authenticated user
        service: Sprint service instance
        session: Database session

    Returns:
        Updated sprint details
    """
    # Get sprint and verify team access
    sprint = await service._get_sprint_by_id(session, sprint_id)
    if not sprint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sprint not found"
        )
    await verify_team_access(sprint.team_id, current_user, session)

    updated_sprint = await service.update_sprint_status(
        session, sprint_id, status_update.status.value
    )
    return SprintResponse.model_validate(updated_sprint)


@router.get("/teams/{team_id}/sprints", response_model=List[SprintResponse])
async def list_sprints(
    team_id: UUID,
    include_closed: Optional[bool] = False,
    current_user: User = Depends(get_current_user),
    service: SprintService = Depends(get_sprint_service),
    session: AsyncSession = Depends(get_db),
) -> List[SprintResponse]:
    """
    List all sprints for a team.

    Parameters:
        team_id: Team ID to list sprints for
        include_closed: Whether to include closed sprints
        current_user: Current authenticated user
        service: Sprint service instance
        session: Database session

    Returns:
        List of sprints for the team
    """
    # Verify team access
    await verify_team_access(team_id, current_user, session)

    sprints = await service.list_team_sprints(session, team_id, include_closed)
    return [SprintResponse.model_validate(sprint) for sprint in sprints]


# Additional endpoints as needed
