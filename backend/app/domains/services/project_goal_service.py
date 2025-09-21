"""ProjectGoal service for business logic operations."""

import uuid
from typing import Optional

import structlog
from sqlalchemy import and_, desc, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthorizationError, DatabaseError, ValidationError
from app.core.performance import monitor_performance
from app.domains.models.project_goal import ProjectGoal
from app.domains.models.team import TeamMember, TeamRole
from app.domains.schemas.project_goal import (
    ProjectGoalCreateRequest,
    ProjectGoalListResponse,
    ProjectGoalResponse,
    ProjectGoalUpdateRequest,
)

logger = structlog.get_logger(__name__)


class ProjectGoalService:
    """Service for project goal operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize project goal service with database session."""
        self.db = db

    async def get_project_goals(
        self,
        team_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> ProjectGoalListResponse:
        """
        Get all project goals for a team, ordered by priority.

        Args:
            team_id: Team UUID
            user_id: Current user UUID (for authorization)

        Returns:
            ProjectGoalListResponse with all team goals

        Raises:
            AuthorizationError: If user is not a team member
        """
        logger.info(
            "Fetching project goals",
            team_id=str(team_id),
            user_id=str(user_id),
        )

        # Verify user is team member (AC2: all team members can view goals)
        if not await self._is_team_member(team_id, user_id):
            raise AuthorizationError(
                message="You must be a team member to view team goals",
                error_code="NOT_TEAM_MEMBER",
                details={"team_id": str(team_id), "user_id": str(user_id)},
                recovery_action="Please join the team or contact the team owner",
            )

        # Query goals ordered by priority_weight (highest first) then created_at
        query = (
            select(ProjectGoal)
            .where(ProjectGoal.team_id == team_id)
            .order_by(desc(ProjectGoal.priority_weight), ProjectGoal.created_at)
        )

        result = await self.db.execute(query)
        goals = result.scalars().all()

        # Convert to response format
        goal_responses = [ProjectGoalResponse.model_validate(goal) for goal in goals]

        logger.info(
            "Successfully fetched project goals",
            team_id=str(team_id),
            user_id=str(user_id),
            goal_count=len(goal_responses),
        )

        return ProjectGoalListResponse(goals=goal_responses, total=len(goal_responses))

    @monitor_performance("project_goal_creation")
    async def create_project_goal(
        self,
        team_id: uuid.UUID,
        goal_data: ProjectGoalCreateRequest,
        author_id: uuid.UUID,
    ) -> ProjectGoalResponse:
        """
        Create a new project goal.

        Args:
            team_id: Team UUID to create goal for
            goal_data: Goal creation data
            author_id: ID of the user creating the goal

        Returns:
            ProjectGoalResponse: Created goal

        Raises:
            AuthorizationError: If user doesn't have permission to create goals
            ValidationError: If goal description is duplicate for this team
            DatabaseError: If database operation fails
        """
        logger.info(
            "Creating project goal",
            team_id=str(team_id),
            author_id=str(author_id),
            priority_weight=goal_data.priority_weight,
        )

        # Verify user has goal management permissions (AC2: PO/Owner only)
        user_role = await self._get_user_team_role(team_id, author_id)
        if not self._can_manage_goals(user_role):
            raise AuthorizationError(
                message="Only Product Owners and Team Owners can manage goals",
                error_code="INSUFFICIENT_PERMISSIONS",
                details={
                    "team_id": str(team_id),
                    "user_id": str(author_id),
                    "user_role": user_role.value if user_role else None,
                    "required_roles": [TeamRole.OWNER.value],
                },
                recovery_action="Please contact a team owner to create goals",
            )

        # Check for duplicate goal description (AC3: uniqueness validation)
        await self._validate_goal_uniqueness(team_id, goal_data.description, None)

        try:
            # Create new goal
            new_goal = ProjectGoal(
                team_id=team_id,
                description=goal_data.description,
                priority_weight=goal_data.priority_weight,
                success_metrics=goal_data.success_metrics,
                author_id=author_id,
                created_by=author_id,
                updated_by=None,
            )

            self.db.add(new_goal)
            await self.db.commit()
            await self.db.refresh(new_goal)

            logger.info(
                "Project goal created successfully",
                goal_id=str(new_goal.id),
                team_id=str(team_id),
                author_id=str(author_id),
                priority_weight=new_goal.priority_weight,
            )

            return ProjectGoalResponse.model_validate(new_goal)

        except IntegrityError as e:
            await self.db.rollback()
            logger.error(
                "Database integrity error creating project goal",
                error=str(e),
                team_id=str(team_id),
                author_id=str(author_id),
            )
            raise DatabaseError(
                message="Failed to create project goal due to data constraints",
                error_code="GOAL_CREATION_CONSTRAINT_ERROR",
                details={"original_error": str(e)},
                recovery_action="Please check your input and try again",
            )
        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Unexpected error creating project goal",
                error=str(e),
                error_type=type(e).__name__,
                team_id=str(team_id),
                author_id=str(author_id),
            )
            raise DatabaseError(
                message="An unexpected error occurred while creating the goal",
                error_code="GOAL_CREATION_ERROR",
                details={"original_error": str(e)},
                recovery_action="Please try again or contact support",
            )

    @monitor_performance("project_goal_update")
    async def update_project_goal(
        self,
        team_id: uuid.UUID,
        goal_id: uuid.UUID,
        goal_data: ProjectGoalUpdateRequest,
        user_id: uuid.UUID,
    ) -> ProjectGoalResponse:
        """
        Update an existing project goal.

        Args:
            team_id: Team UUID containing the goal
            goal_id: Goal UUID to update
            goal_data: Goal update data
            user_id: ID of the user updating the goal

        Returns:
            ProjectGoalResponse: Updated goal

        Raises:
            AuthorizationError: If user doesn't have permission to update goals
            ValidationError: If goal not found or validation fails
            DatabaseError: If database operation fails
        """
        logger.info(
            "Updating project goal",
            goal_id=str(goal_id),
            team_id=str(team_id),
            user_id=str(user_id),
        )

        # Verify user has goal management permissions
        user_role = await self._get_user_team_role(team_id, user_id)
        if not self._can_manage_goals(user_role):
            raise AuthorizationError(
                message="Only Product Owners and Team Owners can manage goals",
                error_code="INSUFFICIENT_PERMISSIONS",
                details={
                    "team_id": str(team_id),
                    "user_id": str(user_id),
                    "user_role": user_role.value if user_role else None,
                },
                recovery_action="Please contact a team owner to update goals",
            )

        # Get existing goal
        query = select(ProjectGoal).where(
            and_(ProjectGoal.id == goal_id, ProjectGoal.team_id == team_id)
        )
        result = await self.db.execute(query)
        existing_goal = result.scalar_one_or_none()

        if not existing_goal:
            raise ValidationError(
                message="Goal not found",
                error_code="GOAL_NOT_FOUND",
                details={"goal_id": str(goal_id), "team_id": str(team_id)},
                recovery_action="Please verify the goal ID and try again",
            )

        # Validate uniqueness if description is being changed
        if goal_data.description and goal_data.description != existing_goal.description:
            await self._validate_goal_uniqueness(
                team_id, goal_data.description, goal_id
            )

        try:
            # Update goal fields
            if goal_data.description is not None:
                existing_goal.description = goal_data.description
            if goal_data.priority_weight is not None:
                existing_goal.priority_weight = goal_data.priority_weight
            if goal_data.success_metrics is not None:
                existing_goal.success_metrics = goal_data.success_metrics

            existing_goal.updated_by = user_id

            await self.db.commit()
            await self.db.refresh(existing_goal)

            logger.info(
                "Project goal updated successfully",
                goal_id=str(goal_id),
                team_id=str(team_id),
                user_id=str(user_id),
            )

            return ProjectGoalResponse.model_validate(existing_goal)

        except IntegrityError as e:
            await self.db.rollback()
            logger.error(
                "Database integrity error updating project goal",
                error=str(e),
                goal_id=str(goal_id),
                team_id=str(team_id),
                user_id=str(user_id),
            )
            raise DatabaseError(
                message="Failed to update project goal due to data constraints",
                error_code="GOAL_UPDATE_CONSTRAINT_ERROR",
                details={"original_error": str(e)},
                recovery_action="Please check your input and try again",
            )

    async def delete_project_goal(
        self,
        team_id: uuid.UUID,
        goal_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> None:
        """
        Delete a project goal.

        Args:
            team_id: Team UUID containing the goal
            goal_id: Goal UUID to delete
            user_id: ID of the user deleting the goal

        Raises:
            AuthorizationError: If user doesn't have permission to delete goals
            ValidationError: If goal not found
            DatabaseError: If database operation fails
        """
        logger.info(
            "Deleting project goal",
            goal_id=str(goal_id),
            team_id=str(team_id),
            user_id=str(user_id),
        )

        # Verify user has goal management permissions
        user_role = await self._get_user_team_role(team_id, user_id)
        if not self._can_manage_goals(user_role):
            raise AuthorizationError(
                message="Only Product Owners and Team Owners can manage goals",
                error_code="INSUFFICIENT_PERMISSIONS",
                details={
                    "team_id": str(team_id),
                    "user_id": str(user_id),
                    "user_role": user_role.value if user_role else None,
                },
                recovery_action="Please contact a team owner to delete goals",
            )

        # Get existing goal to verify it exists
        query = select(ProjectGoal).where(
            and_(ProjectGoal.id == goal_id, ProjectGoal.team_id == team_id)
        )
        result = await self.db.execute(query)
        existing_goal = result.scalar_one_or_none()

        if not existing_goal:
            raise ValidationError(
                message="Goal not found",
                error_code="GOAL_NOT_FOUND",
                details={"goal_id": str(goal_id), "team_id": str(team_id)},
                recovery_action="Please verify the goal ID and try again",
            )

        try:
            await self.db.delete(existing_goal)
            await self.db.commit()

            logger.info(
                "Project goal deleted successfully",
                goal_id=str(goal_id),
                team_id=str(team_id),
                user_id=str(user_id),
            )

        except Exception as e:
            await self.db.rollback()
            logger.error(
                "Unexpected error deleting project goal",
                error=str(e),
                error_type=type(e).__name__,
                goal_id=str(goal_id),
                team_id=str(team_id),
                user_id=str(user_id),
            )
            raise DatabaseError(
                message="An unexpected error occurred while deleting the goal",
                error_code="GOAL_DELETION_ERROR",
                details={"original_error": str(e)},
                recovery_action="Please try again or contact support",
            )

    async def _is_team_member(self, team_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Check if user is a member of the team."""
        query = select(TeamMember).where(
            and_(TeamMember.team_id == team_id, TeamMember.user_id == user_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def _get_user_team_role(
        self, team_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[TeamRole]:
        """Get user's role in the team."""
        query = select(TeamMember.role).where(
            and_(TeamMember.team_id == team_id, TeamMember.user_id == user_id)
        )
        result = await self.db.execute(query)
        role = result.scalar_one_or_none()
        return TeamRole(role) if role else None

    def _can_manage_goals(self, role: Optional[TeamRole]) -> bool:
        """Check if role can manage goals (PO/Owner permissions)."""
        # AC2: Product Owners and Team Owners can create, edit, delete goals
        # For now, we only have OWNER and MEMBER roles, but this is extensible
        return role == TeamRole.OWNER

    async def _validate_goal_uniqueness(
        self,
        team_id: uuid.UUID,
        description: str,
        exclude_goal_id: Optional[uuid.UUID] = None,
    ) -> None:
        """
        Validate that goal description is unique within the team.

        Args:
            team_id: Team UUID
            description: Goal description to check
            exclude_goal_id: Goal ID to exclude from check (for updates)

        Raises:
            ValidationError: If duplicate goal exists
        """
        query = select(ProjectGoal).where(
            and_(
                ProjectGoal.team_id == team_id,
                func.lower(func.trim(ProjectGoal.description))
                == func.lower(func.trim(description)),
            )
        )

        if exclude_goal_id:
            query = query.where(ProjectGoal.id != exclude_goal_id)

        result = await self.db.execute(query)
        existing_goal = result.scalar_one_or_none()

        if existing_goal:
            raise ValidationError(
                message="A goal with this description already exists for this team",
                error_code="DUPLICATE_GOAL",
                details={
                    "existing_goal_id": str(existing_goal.id),
                    "team_id": str(team_id),
                    "description": description,
                },
                recovery_action="Please modify the goal description or update the existing goal",
            )
