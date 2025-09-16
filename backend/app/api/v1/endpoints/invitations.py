"""Invitation endpoints for team invitation management."""

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.domains.models.user import User
from app.domains.schemas.invitation import (
    InvitationCreateRequest,
    InvitationCreateResponse,
    InvitationListResponse,
)
from app.domains.services.invitation_service import InvitationService
from app.domains.services.team_service import TeamService
from app.infra.db import get_session

logger = structlog.get_logger(__name__)

router = APIRouter()


async def get_invitation_service(
    db: AsyncSession = Depends(get_session),
) -> InvitationService:
    """Dependency to get invitation service with database session."""
    return InvitationService(db)


async def get_team_service(db: AsyncSession = Depends(get_session)) -> TeamService:
    """Dependency to get team service with database session."""
    return TeamService(db)


@router.post(
    "/{team_id}/invitations",
    response_model=InvitationCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a team invitation",
    description="Send an invitation to join a team. Only team owners can send.",
)
async def create_invitation(
    team_id: str,
    invitation_data: InvitationCreateRequest,
    current_user: User = Depends(get_current_user),
    invitation_service: InvitationService = Depends(get_invitation_service),
    team_service: TeamService = Depends(get_team_service),
) -> InvitationCreateResponse:
    """Create a new team invitation.

    Args:
        team_id: UUID of the team to invite to
        invitation_data: Invitation creation data
        current_user: Currently authenticated user
        invitation_service: Invitation service dependency
        team_service: Team service dependency

    Returns:
        InvitationCreateResponse: The created invitation data with success message

    Raises:
        HTTPException: 403 if not team owner, 409 if user already member or
            invitation exists
    """
    logger.info(
        "Invitation creation attempt",
        team_id=team_id,
        email=invitation_data.email,
        inviter_id=str(current_user.id),
    )

    try:
        import uuid

        team_uuid = uuid.UUID(team_id)

        # Check if current user is team owner
        if not await team_service.is_user_team_owner(team_uuid, current_user.id):
            logger.warning(
                "Unauthorized invitation attempt - user not team owner",
                team_id=team_id,
                user_id=str(current_user.id),
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only team owners can send invitations",
            )

        # Create the invitation
        invitation = await invitation_service.create_invitation(
            team_uuid, invitation_data, current_user
        )

        logger.info(
            "Invitation creation successful",
            invitation_id=str(invitation.id),
            team_id=team_id,
            email=invitation_data.email,
            inviter_id=str(current_user.id),
        )

        return InvitationCreateResponse(
            message="Invitation sent successfully", invitation=invitation
        )

    except ValueError as e:
        error_message = str(e)
        if "already a member" in error_message:
            logger.warning(
                "Invitation failed - user already team member",
                team_id=team_id,
                email=invitation_data.email,
                inviter_id=str(current_user.id),
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This user is already a member of this team",
            )
        elif "already been sent" in error_message:
            logger.warning(
                "Invitation failed - invitation already exists",
                team_id=team_id,
                email=invitation_data.email,
                inviter_id=str(current_user.id),
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An invitation has already been sent to this email",
            )
        else:
            logger.warning(
                "Invitation creation failed - validation error",
                error=error_message,
                team_id=team_id,
                inviter_id=str(current_user.id),
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message,
            )

    except Exception as e:
        logger.error(
            "Invitation creation failed - unexpected error",
            error=str(e),
            team_id=team_id,
            inviter_id=str(current_user.id),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during invitation creation",
        )


@router.get(
    "/{team_id}/invitations",
    response_model=InvitationListResponse,
    summary="List team invitations",
    description="Get all pending invitations for a team. Only owners can view.",
)
async def list_team_invitations(
    team_id: str,
    current_user: User = Depends(get_current_user),
    invitation_service: InvitationService = Depends(get_invitation_service),
    team_service: TeamService = Depends(get_team_service),
) -> InvitationListResponse:
    """Get all pending invitations for a team.

    Args:
        team_id: UUID of the team
        current_user: Currently authenticated user
        invitation_service: Invitation service dependency
        team_service: Team service dependency

    Returns:
        InvitationListResponse: List of pending invitations with inviter names

    Raises:
        HTTPException: 403 if not team owner, 404 if team not found
    """
    logger.info(
        "Team invitations list request",
        team_id=team_id,
        user_id=str(current_user.id),
    )

    try:
        import uuid

        team_uuid = uuid.UUID(team_id)

        # Check if current user is team owner
        if not await team_service.is_user_team_owner(team_uuid, current_user.id):
            logger.warning(
                "Unauthorized invitation list access - user not team owner",
                team_id=team_id,
                user_id=str(current_user.id),
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only team owners can view invitations",
            )

        # Get team invitations
        invitations = await invitation_service.get_team_invitations(team_uuid)

        logger.info(
            "Team invitations list successful",
            team_id=team_id,
            invitation_count=len(invitations),
            user_id=str(current_user.id),
        )

        return InvitationListResponse(invitations=invitations)

    except ValueError as e:
        logger.warning(
            "Team invitations list failed - validation error",
            error=str(e),
            team_id=team_id,
            user_id=str(current_user.id),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception as e:
        logger.error(
            "Team invitations list failed - unexpected error",
            error=str(e),
            team_id=team_id,
            user_id=str(current_user.id),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during invitation list retrieval",
        )
