"""Velocity-related API endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.velocity import VelocityResponse
from app.services.velocity_service import VelocityService

router = APIRouter(prefix="/teams", tags=["velocity"])


def get_velocity_service(db: AsyncSession = Depends(get_db)) -> VelocityService:
    """Get velocity service instance."""
    return VelocityService(db)


@router.get(
    "/{team_id}/velocity",
    response_model=List[VelocityResponse],
    name="Get team velocity",
)
async def get_team_velocity(
    team_id: str,
    limit: int = 5,
    current_user: User = Depends(get_current_user),
    velocity_service: VelocityService = Depends(get_velocity_service),
) -> List[VelocityResponse]:
    """Get velocity data for a team's recent sprints.

    Args:
        team_id: The team's ID
        limit: Maximum number of sprints to return (default: 5)
        current_user: The authenticated user
        velocity_service: The velocity service instance

    Returns:
        List of velocity data for each sprint

    Raises:
        HTTPException: If team not found or user not authorized
    """
    try:
        return await velocity_service.get_team_velocity(team_id, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve velocity data: {str(e)}",
        )
