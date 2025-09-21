"""Teams-related API endpoints including work item management."""

import uuid
from typing import Any, Dict

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.exceptions import (
    AuthorizationError,
    DatabaseError,
    ValidationError,
    format_error_response,
    get_http_status_for_error_code,
)
from app.domains.models.user import User
from app.domains.schemas.project_goal import (
    ProjectGoalCreateRequest,
    ProjectGoalListResponse,
    ProjectGoalResponse,
    ProjectGoalUpdateRequest,
)
from app.domains.schemas.team import TeamResponse
from app.domains.schemas.work_item import WorkItemCreateRequest, WorkItemResponse
from app.domains.services.project_goal_service import ProjectGoalService
from app.domains.services.team_service import TeamService
from app.domains.services.work_item_service import WorkItemService
from app.infra.db import get_session

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/teams", tags=["teams"])


async def get_work_item_service(
    db: AsyncSession = Depends(get_session),
) -> WorkItemService:
    """Dependency to get work item service with database session."""
    return WorkItemService(db)


async def get_team_service(
    db: AsyncSession = Depends(get_session),
) -> TeamService:
    """Dependency to get team service with database session."""
    return TeamService(db)


async def get_project_goal_service(
    db: AsyncSession = Depends(get_session),
) -> ProjectGoalService:
    """Dependency to get project goal service with database session."""
    return ProjectGoalService(db)


@router.post(
    "/{team_id}/work-items",
    response_model=WorkItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new work item",
    description="Create a new work item in the team's backlog. "
    "The item will be automatically assigned the highest priority for top placement.",
)
async def create_work_item(
    team_id: uuid.UUID,
    work_item_data: WorkItemCreateRequest,
    current_user: User = Depends(get_current_user),
    work_item_service: WorkItemService = Depends(get_work_item_service),
) -> WorkItemResponse:
    """
    Create a new work item for a team.

    This endpoint addresses Story 2.3: Create Work Item requirements including:
    - Team membership authorization (AC 5)
    - Atomic priority calculation for top placement (AC 4)
    - Comprehensive validation and error handling (AC 2, 6, 8)
    - Author attribution (AC 5)
    - Performance monitoring (<1 second requirement)

    Args:
        team_id: UUID of the team to create the work item in
        work_item_data: Work item creation request data
        current_user: Authenticated user making the request
        work_item_service: Work item service dependency

    Returns:
        WorkItemResponse: The created work item with auto-assigned priority

    Raises:
        HTTPException: Various errors with specific error codes and recovery actions
    """
    logger.info(
        "Creating work item",
        team_id=str(team_id),
        user_id=str(current_user.id),
        title=work_item_data.title,
        work_item_type=work_item_data.type,
    )

    try:
        # Validate team_id matches the one in the request body
        if work_item_data.team_id != team_id:
            logger.warning(
                "Team ID mismatch",
                url_team_id=str(team_id),
                body_team_id=str(work_item_data.team_id),
            )
            raise ValidationError(
                message="Team ID in URL does not match team ID in request body.",
                error_code="VALIDATION_TEAM_ID_MISMATCH",
                details={
                    "url_team_id": str(team_id),
                    "body_team_id": str(work_item_data.team_id),
                },
                recovery_action="Please ensure the team ID in the URL matches the request data.",
            )

        # Create work item using service (includes all QA concern mitigations)
        work_item = await work_item_service.create_work_item(
            work_item_data=work_item_data,
            author_id=current_user.id,
        )

        logger.info(
            "Work item created successfully",
            work_item_id=str(work_item.id),
            team_id=str(team_id),
            user_id=str(current_user.id),
            priority=work_item.priority,
        )

        # Ensure return type matches endpoint declaration
        # The service already returns WorkItemResponse, but mypy needs explicit casting
        return (
            WorkItemResponse.model_validate(work_item)
            if hasattr(work_item, "model_dump")
            else work_item
        )

    except (AuthorizationError, ValidationError, DatabaseError) as e:
        # Log the specific error for debugging
        logger.error(
            "Work item creation failed",
            error_code=e.error_code,
            error_message=e.message,
            team_id=str(team_id),
            user_id=str(current_user.id),
            error_details=e.details,
        )

        # Return structured error response
        error_response = format_error_response(e)
        http_status = get_http_status_for_error_code(e.error_code)

        raise HTTPException(
            status_code=http_status,
            detail=error_response["error"],
        )

    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(
            "Unexpected error during work item creation",
            error=str(e),
            error_type=type(e).__name__,
            team_id=str(team_id),
            user_id=str(current_user.id),
        )

        # Return generic error for security
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred while creating the work item.",
                "recovery_action": "Please try again. If the problem persists, contact support.",
            },
        )


@router.patch(
    "/{team_id}/work-items/{work_item_id}/archive",
    response_model=WorkItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Archive a work item",
    description="Archive a work item by setting its status to 'archived' (soft delete). "
    "The work item remains in the database but is excluded from regular views.",
)
async def archive_work_item(
    team_id: uuid.UUID,
    work_item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    work_item_service: WorkItemService = Depends(get_work_item_service),
) -> WorkItemResponse:
    """
    Archive a work item for a team.

    This endpoint implements Story 2.5: Soft-Delete Work Item requirements:
    - Team membership authorization (AC 1)
    - Soft delete by setting status to 'archived' (AC 3)
    - Returns updated work item for UI updates (AC 6)
    - Maintains data integrity and audit trail (AC 3)
    - Error handling with clear messages (AC 8)

    Args:
        team_id: UUID of the team containing the work item
        work_item_id: UUID of the work item to archive
        current_user: Authenticated user making the request
        work_item_service: Work item service dependency

    Returns:
        WorkItemResponse: The archived work item with status='archived'

    Raises:
        HTTPException: Various errors including authorization and not found
    """
    logger.info(
        "Archiving work item",
        team_id=str(team_id),
        work_item_id=str(work_item_id),
        user_id=str(current_user.id),
    )

    try:
        # Archive work item using service
        archived_item = await work_item_service.archive_work_item(
            work_item_id=work_item_id,
            user_id=current_user.id,
        )

        logger.info(
            "Work item archived successfully",
            work_item_id=str(work_item_id),
            team_id=str(team_id),
            user_id=str(current_user.id),
            new_status=archived_item.status,
        )

        return archived_item

    except ValueError as e:
        # Handle not found or authorization errors
        error_message = str(e)

        if "not found" in error_message.lower():
            logger.warning(
                "Work item not found for archiving",
                work_item_id=str(work_item_id),
                team_id=str(team_id),
                user_id=str(current_user.id),
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "WORK_ITEM_NOT_FOUND",
                    "message": "The requested work item was not found.",
                    "recovery_action": "Please verify the work item ID and try again.",
                },
            )
        elif "not a member" in error_message.lower():
            logger.warning(
                "Unauthorized archive attempt",
                work_item_id=str(work_item_id),
                team_id=str(team_id),
                user_id=str(current_user.id),
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "NOT_TEAM_MEMBER",
                    "message": "You must be a team member to archive work items.",
                    "recovery_action": "Please join the team or contact the team owner.",
                },
            )
        else:
            # Generic ValueError
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "ARCHIVE_FAILED",
                    "message": error_message,
                    "recovery_action": "Please check your request and try again.",
                },
            )

    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(
            "Unexpected error during work item archival",
            error=str(e),
            error_type=type(e).__name__,
            work_item_id=str(work_item_id),
            team_id=str(team_id),
            user_id=str(current_user.id),
        )

        # Return generic error for security
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred while archiving the work item.",
                "recovery_action": "Please try again. If the problem persists, contact support.",
            },
        )


@router.get(
    "/{team_id}/goals",
    response_model=ProjectGoalListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get project goals for team",
    description="Retrieve all project goals for a team, ordered by priority. "
    "All team members can view goals.",
)
async def get_project_goals(
    team_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    goal_service: ProjectGoalService = Depends(get_project_goal_service),
) -> ProjectGoalListResponse:
    """
    Get all project goals for a team.

    This endpoint implements Story 3.1 AC2: Goal Management Interface requirements:
    - All team members can view goals
    - Goals returned ordered by priority weight (highest first)
    - Proper team membership authorization

    Args:
        team_id: UUID of the team to get goals for
        current_user: Authenticated user making the request
        goal_service: Project goal service dependency

    Returns:
        ProjectGoalListResponse: List of team goals with metadata

    Raises:
        HTTPException: 403 if user is not a team member
    """
    logger.info(
        "Fetching project goals",
        team_id=str(team_id),
        user_id=str(current_user.id),
    )

    try:
        goals = await goal_service.get_project_goals(
            team_id=team_id,
            user_id=current_user.id,
        )

        logger.info(
            "Project goals fetched successfully",
            team_id=str(team_id),
            user_id=str(current_user.id),
            goal_count=goals.total,
        )

        return goals

    except (AuthorizationError, ValidationError, DatabaseError) as e:
        logger.error(
            "Project goals fetch failed",
            error_code=e.error_code,
            error_message=e.message,
            team_id=str(team_id),
            user_id=str(current_user.id),
            error_details=e.details,
        )

        error_response = format_error_response(e)
        http_status = get_http_status_for_error_code(e.error_code)

        raise HTTPException(
            status_code=http_status,
            detail=error_response["error"],
        )

    except Exception as e:
        logger.error(
            "Unexpected error fetching project goals",
            error=str(e),
            error_type=type(e).__name__,
            team_id=str(team_id),
            user_id=str(current_user.id),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred while fetching project goals.",
                "recovery_action": "Please try again. If the problem persists, contact support.",
            },
        )


@router.post(
    "/{team_id}/goals",
    response_model=ProjectGoalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project goal",
    description="Create a new strategic goal for a team. "
    "Only Product Owners and Team Owners can create goals.",
)
async def create_project_goal(
    team_id: uuid.UUID,
    goal_data: ProjectGoalCreateRequest,
    current_user: User = Depends(get_current_user),
    goal_service: ProjectGoalService = Depends(get_project_goal_service),
) -> ProjectGoalResponse:
    """
    Create a new project goal for a team.

    This endpoint implements Story 3.1 AC2 & AC3: Goal Management Interface requirements:
    - Only Product Owners and Team Owners can create goals
    - Goal content validation including uniqueness checks
    - Priority weighting (1-10 scale)
    - Rich text descriptions with 500 char limit
    - Author attribution and audit trail

    Args:
        team_id: UUID of the team to create the goal for
        goal_data: Goal creation request data
        current_user: Authenticated user making the request
        goal_service: Project goal service dependency

    Returns:
        ProjectGoalResponse: The created goal with auto-generated ID and timestamps

    Raises:
        HTTPException: Various errors with specific error codes and recovery actions
    """
    logger.info(
        "Creating project goal",
        team_id=str(team_id),
        user_id=str(current_user.id),
        priority_weight=goal_data.priority_weight,
    )

    try:
        new_goal = await goal_service.create_project_goal(
            team_id=team_id,
            goal_data=goal_data,
            author_id=current_user.id,
        )

        logger.info(
            "Project goal created successfully",
            goal_id=str(new_goal.id),
            team_id=str(team_id),
            user_id=str(current_user.id),
            priority_weight=new_goal.priority_weight,
        )

        return new_goal

    except (AuthorizationError, ValidationError, DatabaseError) as e:
        logger.error(
            "Project goal creation failed",
            error_code=e.error_code,
            error_message=e.message,
            team_id=str(team_id),
            user_id=str(current_user.id),
            error_details=e.details,
        )

        error_response = format_error_response(e)
        http_status = get_http_status_for_error_code(e.error_code)

        raise HTTPException(
            status_code=http_status,
            detail=error_response["error"],
        )

    except Exception as e:
        logger.error(
            "Unexpected error creating project goal",
            error=str(e),
            error_type=type(e).__name__,
            team_id=str(team_id),
            user_id=str(current_user.id),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred while creating the project goal.",
                "recovery_action": "Please try again. If the problem persists, contact support.",
            },
        )


@router.put(
    "/{team_id}/goals/{goal_id}",
    response_model=ProjectGoalResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a project goal",
    description="Update an existing project goal. "
    "Only Product Owners and Team Owners can update goals.",
)
async def update_project_goal(
    team_id: uuid.UUID,
    goal_id: uuid.UUID,
    goal_data: ProjectGoalUpdateRequest,
    current_user: User = Depends(get_current_user),
    goal_service: ProjectGoalService = Depends(get_project_goal_service),
) -> ProjectGoalResponse:
    """
    Update an existing project goal.

    This endpoint implements Story 3.1 AC2 & AC3: Goal Management Interface requirements:
    - Only Product Owners and Team Owners can update goals
    - Partial updates supported (only provided fields are updated)
    - Goal uniqueness validation if description changes
    - Audit trail with updated_by tracking

    Args:
        team_id: UUID of the team containing the goal
        goal_id: UUID of the goal to update
        goal_data: Goal update request data
        current_user: Authenticated user making the request
        goal_service: Project goal service dependency

    Returns:
        ProjectGoalResponse: The updated goal with new timestamps

    Raises:
        HTTPException: Various errors including authorization, not found, and validation
    """
    logger.info(
        "Updating project goal",
        goal_id=str(goal_id),
        team_id=str(team_id),
        user_id=str(current_user.id),
    )

    try:
        updated_goal = await goal_service.update_project_goal(
            team_id=team_id,
            goal_id=goal_id,
            goal_data=goal_data,
            user_id=current_user.id,
        )

        logger.info(
            "Project goal updated successfully",
            goal_id=str(goal_id),
            team_id=str(team_id),
            user_id=str(current_user.id),
        )

        return updated_goal

    except (AuthorizationError, ValidationError, DatabaseError) as e:
        logger.error(
            "Project goal update failed",
            error_code=e.error_code,
            error_message=e.message,
            goal_id=str(goal_id),
            team_id=str(team_id),
            user_id=str(current_user.id),
            error_details=e.details,
        )

        error_response = format_error_response(e)
        http_status = get_http_status_for_error_code(e.error_code)

        raise HTTPException(
            status_code=http_status,
            detail=error_response["error"],
        )

    except Exception as e:
        logger.error(
            "Unexpected error updating project goal",
            error=str(e),
            error_type=type(e).__name__,
            goal_id=str(goal_id),
            team_id=str(team_id),
            user_id=str(current_user.id),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred while updating the project goal.",
                "recovery_action": "Please try again. If the problem persists, contact support.",
            },
        )


@router.delete(
    "/{team_id}/goals/{goal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project goal",
    description="Delete an existing project goal. "
    "Only Product Owners and Team Owners can delete goals.",
)
async def delete_project_goal(
    team_id: uuid.UUID,
    goal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    goal_service: ProjectGoalService = Depends(get_project_goal_service),
) -> None:
    """
    Delete a project goal.

    This endpoint implements Story 3.1 AC2: Goal Management Interface requirements:
    - Only Product Owners and Team Owners can delete goals
    - Hard delete for simplicity (goal is permanently removed)
    - Proper authorization and error handling

    Args:
        team_id: UUID of the team containing the goal
        goal_id: UUID of the goal to delete
        current_user: Authenticated user making the request
        goal_service: Project goal service dependency

    Returns:
        None (204 No Content on success)

    Raises:
        HTTPException: Various errors including authorization and not found
    """
    logger.info(
        "Deleting project goal",
        goal_id=str(goal_id),
        team_id=str(team_id),
        user_id=str(current_user.id),
    )

    try:
        await goal_service.delete_project_goal(
            team_id=team_id,
            goal_id=goal_id,
            user_id=current_user.id,
        )

        logger.info(
            "Project goal deleted successfully",
            goal_id=str(goal_id),
            team_id=str(team_id),
            user_id=str(current_user.id),
        )

    except (AuthorizationError, ValidationError, DatabaseError) as e:
        logger.error(
            "Project goal deletion failed",
            error_code=e.error_code,
            error_message=e.message,
            goal_id=str(goal_id),
            team_id=str(team_id),
            user_id=str(current_user.id),
            error_details=e.details,
        )

        error_response = format_error_response(e)
        http_status = get_http_status_for_error_code(e.error_code)

        raise HTTPException(
            status_code=http_status,
            detail=error_response["error"],
        )

    except Exception as e:
        logger.error(
            "Unexpected error deleting project goal",
            error=str(e),
            error_type=type(e).__name__,
            goal_id=str(goal_id),
            team_id=str(team_id),
            user_id=str(current_user.id),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred while deleting the project goal.",
                "recovery_action": "Please try again. If the problem persists, contact support.",
            },
        )


@router.get(
    "/{team_id}",
    response_model=TeamResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "Team not found"},
        403: {"description": "Forbidden - No access to team"},
        401: {"description": "Unauthorized"},
    },
    summary="Get team by ID",
    description="Retrieve a team's details by its ID. Team members can view team details.",
)
async def get_team_by_id(
    team_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service),
) -> TeamResponse:
    """
    Get a team by its ID.

    Args:
        team_id: UUID of the team to retrieve
        current_user: Authenticated user making the request
        team_service: Team service dependency

    Returns:
        TeamResponse: The requested team's details

    Raises:
        HTTPException: 404 if team not found, 403 if user doesn't have access
    """
    logger.info(
        "Fetching team",
        team_id=str(team_id),
        user_id=str(current_user.id),
    )

    try:
        # Get team with members
        team = await team_service.get_team_by_id(team_id)
        if not team:
            logger.warning(
                "Team not found",
                team_id=str(team_id),
                user_id=str(current_user.id),
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "TEAM_NOT_FOUND",
                    "message": "Team not found",
                    "recovery_action": "Please verify the team ID and try again.",
                },
            )

        # Check if user has access to team
        user_member = next(
            (member for member in team.members if member.user_id == current_user.id),
            None,
        )
        if not user_member:
            logger.warning(
                "Unauthorized team access attempt",
                team_id=str(team_id),
                user_id=str(current_user.id),
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "NOT_TEAM_MEMBER",
                    "message": "You do not have access to this team.",
                    "recovery_action": "Please request access from the team owner.",
                },
            )

        logger.info(
            "Team fetched successfully",
            team_id=str(team_id),
            user_id=str(current_user.id),
        )

        return TeamResponse.model_validate(team)

    except HTTPException:
        raise

    except Exception as e:
        logger.error(
            "Unexpected error fetching team",
            error=str(e),
            error_type=type(e).__name__,
            team_id=str(team_id),
            user_id=str(current_user.id),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred while fetching the team.",
                "recovery_action": "Please try again. If the problem persists, contact support.",
            },
        )


@router.get(
    "/{team_id}",
    response_model=TeamResponse,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"description": "Team not found"},
        403: {"description": "Forbidden - No access to team"},
        401: {"description": "Unauthorized"},
    },
    summary="Get team by ID",
    description="Get team details by ID. Requires team membership.",
)
async def get_team_by_id(
    team_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    team_service: TeamService = Depends(get_team_service),
) -> TeamResponse:
    """
    Get a team by its ID.

    Args:
        team_id: UUID of the team to retrieve
        current_user: Authenticated user making the request
        team_service: Team service dependency

    Returns:
        TeamResponse: The requested team's details

    Raises:
        HTTPException: 404 if team not found, 403 if user doesn't have access
    """
    logger.info(
        "Fetching team",
        team_id=str(team_id),
        user_id=str(current_user.id),
    )

    try:
        # Get team with members
        team = await team_service.get_team_by_id(team_id)
        if not team:
            logger.warning(
                "Team not found",
                team_id=str(team_id),
                user_id=str(current_user.id),
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "TEAM_NOT_FOUND",
                    "message": "Team not found",
                    "recovery_action": "Please verify the team ID and try again.",
                },
            )

        # Check if user has access to team
        user_member = next(
            (member for member in team.members if member.user_id == current_user.id),
            None,
        )
        if not user_member:
            logger.warning(
                "Unauthorized team access attempt",
                team_id=str(team_id),
                user_id=str(current_user.id),
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "NOT_TEAM_MEMBER",
                    "message": "You do not have access to this team.",
                    "recovery_action": "Please request access from the team owner.",
                },
            )

        logger.info(
            "Team fetched successfully",
            team_id=str(team_id),
            user_id=str(current_user.id),
        )

        return TeamResponse.model_validate(team)

    except HTTPException:
        raise

    except Exception as e:
        logger.error(
            "Unexpected error fetching team",
            error=str(e),
            error_type=type(e).__name__,
            team_id=str(team_id),
            user_id=str(current_user.id),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred while fetching the team.",
                "recovery_action": "Please try again. If the problem persists, contact support.",
            },
        )


@router.get("/health", include_in_schema=False)
async def teams_health_check() -> Dict[str, Any]:
    """Health check for teams router."""
    return {
        "status": "OK",
        "router": "teams",
        "endpoints": [
            "GET /{team_id}",
            "GET /{team_id}/goals",
            "POST /{team_id}/goals",
            "PUT /{team_id}/goals/{goal_id}",
            "DELETE /{team_id}/goals/{goal_id}",
            "POST /{team_id}/work-items",
            "PATCH /{team_id}/work-items/{work_item_id}/archive",
        ],
    }
