"""Teams endpoints for team creation and management."""

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.domains.models.user import User
from app.domains.schemas.team import TeamCreateRequest, TeamCreateResponse
from app.domains.services.team_service import TeamService
from app.infra.db import get_session

logger = structlog.get_logger(__name__)

router = APIRouter()


async def get_team_service(db: AsyncSession = Depends(get_session)) -> TeamService:
    """Dependency to get team service with database session."""
    return TeamService(db)


@router.post(
    "/",
    response_model=TeamCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new team",
    description="Create a new team with the authenticated user as owner",
)
async def create_team(
    team_data: TeamCreateRequest,
    current_user: User = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service),
) -> TeamCreateResponse:
    """Create a new team with the authenticated user as owner.

    Args:
        team_data: Team creation data
        current_user: Currently authenticated user
        team_service: Team service dependency

    Returns:
        TeamCreateResponse: The created team data with success message

    Raises:
        HTTPException: 409 if team name already exists, 400 for validation errors
    """
    logger.info(
        "Team creation attempt", team_name=team_data.name, user_id=str(current_user.id)
    )

    try:
        # Create the team
        team = await team_service.create_team(team_data, current_user)

        logger.info(
            "Team creation successful",
            team_id=str(team.id),
            team_name=team.name,
            owner_id=str(current_user.id),
        )

        return TeamCreateResponse(message="Team created successfully", team=team)

    except ValueError as e:
        if "already exists" in str(e):
            logger.warning(
                "Team creation failed - name already exists",
                team_name=team_data.name,
                user_id=str(current_user.id),
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Team name '{team_data.name}' already exists for this user",
            )

        logger.warning(
            "Team creation failed - validation error",
            error=str(e),
            user_id=str(current_user.id),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception as e:
        logger.error(
            "Team creation failed - unexpected error",
            error=str(e),
            user_id=str(current_user.id),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during team creation",
        )
