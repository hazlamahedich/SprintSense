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
from app.domains.schemas.work_item import WorkItemCreateRequest, WorkItemResponse
from app.domains.services.work_item_service import WorkItemService
from app.infra.db import get_session

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/teams", tags=["teams"])


async def get_work_item_service(
    db: AsyncSession = Depends(get_session),
) -> WorkItemService:
    """Dependency to get work item service with database session."""
    return WorkItemService(db)


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


@router.get("/health", include_in_schema=False)
async def teams_health_check() -> Dict[str, Any]:
    """Health check for teams router."""
    return {
        "status": "OK",
        "router": "teams",
        "endpoints": [
            "POST /{team_id}/work-items",
            "PATCH /{team_id}/work-items/{work_item_id}/archive",
        ],
    }
