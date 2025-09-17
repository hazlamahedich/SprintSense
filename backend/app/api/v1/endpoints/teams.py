"""Teams endpoints for team creation and management."""

import uuid
from typing import Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.domains.models.user import User
from app.domains.schemas.invitation import (
    InvitationCreateRequest,
    InvitationCreateResponse,
    InvitationListResponse,
)
from app.domains.schemas.team import TeamCreateRequest, TeamCreateResponse
from app.domains.schemas.work_item import (
    WorkItemCreateRequest,
    WorkItemListResponse,
    WorkItemResponse,
)
from app.domains.services.invitation_service import InvitationService
from app.domains.services.team_service import TeamService
from app.domains.services.work_item_service import WorkItemService
from app.infra.db import get_session

logger = structlog.get_logger(__name__)

router = APIRouter()


async def get_team_service(db: AsyncSession = Depends(get_session)) -> TeamService:
    """Dependency to get team service with database session."""
    return TeamService(db)


async def get_invitation_service(
    db: AsyncSession = Depends(get_session),
) -> InvitationService:
    """Dependency to get invitation service with database session."""
    return InvitationService(db)


async def get_work_item_service(
    db: AsyncSession = Depends(get_session),
) -> WorkItemService:
    """Dependency to get work item service with database session."""
    return WorkItemService(db)


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

    except HTTPException:
        # Re-raise HTTPExceptions without modification
        raise
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

    except HTTPException:
        # Re-raise HTTPExceptions without modification
        raise
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


# Work Items Endpoints


@router.get("/{team_id}/work-items", response_model=WorkItemListResponse)
async def get_team_work_items(
    team_id: str,
    limit: int = Query(50, ge=1, le=50, description="Items per page"),
    offset: int = Query(0, ge=0, description="Items to skip for pagination"),
    status: Optional[str] = Query(
        None,
        description="Filter by status (backlog, todo, in_progress, done)",
    ),
    search: Optional[str] = Query(
        None,
        min_length=2,
        description="Search in title and description (minimum 2 characters)",
    ),
    sort_by: str = Query(
        "priority",
        description="Sort field (priority, created_at, story_points, title)",
    ),
    sort_order: str = Query(
        "asc",
        regex="^(asc|desc)$",
        description="Sort direction (asc, desc)",
    ),
    current_user: User = Depends(get_current_user),
    work_item_service: WorkItemService = Depends(get_work_item_service),
) -> WorkItemListResponse:
    """
    Get work items for a team with filtering, sorting, and pagination.

    **Authorization:** User must be a team member.
    **Pagination:** Maximum 50 items per page.
    **Filtering:** By status and text search (min 2 chars).
    **Sorting:** By priority, created_at, story_points, or title.
    """
    logger.info(
        "Work items list request",
        team_id=team_id,
        user_id=str(current_user.id),
    )

    try:
        team_uuid = uuid.UUID(team_id)
        return await work_item_service.get_work_items(
            team_id=team_uuid,
            user_id=current_user.id,
            limit=limit,
            offset=offset,
            status=status,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    except ValueError as e:
        if "not a member" in str(e):
            logger.warning(
                "Unauthorized work items access - user not team member",
                team_id=team_id,
                user_id=str(current_user.id),
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "access_denied",
                    "message": "Not a team member",
                },
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "invalid_parameter",
                    "message": str(e),
                },
            )
    except Exception as e:
        logger.error(
            "Work items list failed - unexpected error",
            error=str(e),
            team_id=team_id,
            user_id=str(current_user.id),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "server_error",
                "message": "Please try again later",
            },
        )


@router.post("/{team_id}/work-items", response_model=WorkItemResponse)
async def create_team_work_item(
    team_id: str,
    work_item_data: WorkItemCreateRequest,
    current_user: User = Depends(get_current_user),
    work_item_service: WorkItemService = Depends(get_work_item_service),
) -> WorkItemResponse:
    """
    Create a new work item for a team.

    **Authorization:** User must be a team member.
    """
    logger.info(
        "Work item creation attempt",
        team_id=team_id,
        user_id=str(current_user.id),
        title=work_item_data.title,
    )

    try:
        team_uuid = uuid.UUID(team_id)

        # Ensure team_id in URL matches team_id in body
        if work_item_data.team_id != team_uuid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "team_id_mismatch",
                    "message": "Team ID in URL must match team ID in body",
                },
            )

        work_item = await work_item_service.create_work_item(
            work_item_data=work_item_data,
            author_id=current_user.id,
        )

        logger.info(
            "Work item creation successful",
            work_item_id=str(work_item.id),
            team_id=team_id,
            user_id=str(current_user.id),
        )

        return work_item

    except ValueError as e:
        if "not a member" in str(e):
            logger.warning(
                "Unauthorized work item creation - user not team member",
                team_id=team_id,
                user_id=str(current_user.id),
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "access_denied",
                    "message": "Not a team member",
                },
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "validation_error",
                    "message": str(e),
                },
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Work item creation failed - unexpected error",
            error=str(e),
            team_id=team_id,
            user_id=str(current_user.id),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "server_error",
                "message": "Please try again later",
            },
        )
