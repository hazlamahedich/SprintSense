"""Work Item service for business logic operations."""

import uuid
from typing import Optional

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthorizationError, DatabaseError
from app.core.performance import measure_performance, monitor_performance
from app.domains.models.team import TeamMember
from app.domains.models.work_item import WorkItem, WorkItemStatus
from app.domains.schemas.work_item import (
    WorkItemCreateRequest,
    WorkItemListResponse,
    WorkItemResponse,
    WorkItemUpdateRequest,
)


class WorkItemService:
    """Service for work item operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize work item service with database session."""
        self.db = db

    async def get_work_items(
        self,
        team_id: uuid.UUID,
        user_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "priority",
        sort_order: str = "asc",
        include_archived: bool = False,
    ) -> WorkItemListResponse:
        """
        Get work items for a team with filtering, sorting, and pagination.

        Args:
            team_id: Team UUID
            user_id: Current user UUID (for authorization)
            limit: Number of items per page (max 50)
            offset: Number of items to skip
            status: Filter by work item status
            search: Search in title and description
            sort_by: Field to sort by (priority, created_at, story_points, title)
            sort_order: Sort direction (asc, desc)
            include_archived: Whether to include archived items (default: False)

        Returns:
            WorkItemListResponse with paginated work items

        Raises:
            ValueError: If user is not a team member
        """
        # Verify user is team member
        if not await self._is_team_member(team_id, user_id):
            raise ValueError("User is not a member of this team")

        # Build base query
        query = select(WorkItem).where(WorkItem.team_id == team_id)

        # Exclude archived items by default unless specifically requested
        if not include_archived:
            query = query.where(WorkItem.status != WorkItemStatus.ARCHIVED)

        # Apply status filter
        if status:
            try:
                status_enum = WorkItemStatus(status)
                query = query.where(WorkItem.status == status_enum)
            except ValueError:
                raise ValueError(f"Invalid status: {status}")

        # Apply search filter
        if search and len(search.strip()) >= 2:
            search_term = f"%{search.strip()}%"
            query = query.where(
                or_(
                    WorkItem.title.ilike(search_term),
                    WorkItem.description.ilike(search_term),
                )
            )

        # Apply sorting
        sort_column = getattr(WorkItem, sort_by, None)
        if sort_column is None:
            sort_column = WorkItem.priority  # Default fallback

        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)

        # Get total count (before pagination)
        count_query = select(WorkItem).where(WorkItem.team_id == team_id)

        # Exclude archived items from count unless specifically requested
        if not include_archived:
            count_query = count_query.where(WorkItem.status != WorkItemStatus.ARCHIVED)

        if status:
            status_enum = WorkItemStatus(status)
            count_query = count_query.where(WorkItem.status == status_enum)
        if search and len(search.strip()) >= 2:
            search_term = f"%{search.strip()}%"
            count_query = count_query.where(
                or_(
                    WorkItem.title.ilike(search_term),
                    WorkItem.description.ilike(search_term),
                )
            )

        total_result = await self.db.execute(count_query)
        total = len(total_result.scalars().all())

        # Apply pagination
        query = query.offset(offset).limit(min(limit, 50))

        # Execute query
        result = await self.db.execute(query)
        work_items = result.scalars().all()

        # Convert to response format
        items = [WorkItemResponse.model_validate(item) for item in work_items]

        return WorkItemListResponse(
            items=items,
            total=total,
            page=(offset // limit) + 1,
            size=len(items),
        )

    @monitor_performance("work_item_creation")
    async def create_work_item(
        self,
        work_item_data: WorkItemCreateRequest,
        author_id: uuid.UUID,
    ) -> WorkItemResponse:
        """
        Create a new work item with atomic priority calculation.

        Args:
            work_item_data: Work item creation data
            author_id: ID of the user creating the work item

        Returns:
            WorkItemResponse: Created work item

        Raises:
            ValueError: If user is not a team member or validation fails
            RuntimeError: If priority calculation fails after retries
        """
        # Verify user is team member with specific error handling
        if not await self._is_team_member(work_item_data.team_id, author_id):
            raise AuthorizationError.not_team_member(
                str(work_item_data.team_id), str(author_id)
            )

        # Calculate priority atomically with retry logic for race conditions
        max_retries = 3
        for attempt in range(max_retries):
            try:
                async with self.db.begin():
                    # Determine priority: use provided value or auto-calculate
                    if work_item_data.priority is not None:
                        # User-provided priority
                        new_priority = work_item_data.priority
                    else:
                        # Auto-calculate priority with performance monitoring
                        async with measure_performance("priority_calculation"):
                            highest_priority = await self._get_highest_priority(
                                work_item_data.team_id
                            )
                        # Calculate new priority (highest + 1 for top placement)
                        new_priority = highest_priority + 1.0

                    # Create work item with calculated/provided priority
                    work_item = WorkItem(
                        team_id=work_item_data.team_id,
                        author_id=author_id,
                        assignee_id=work_item_data.assignee_id,
                        type=work_item_data.type,
                        title=work_item_data.title,
                        description=work_item_data.description,
                        priority=new_priority,
                        story_points=work_item_data.story_points,
                        # Default values for new backlog items
                        status=WorkItemStatus.BACKLOG,
                        sprint_id=None,  # New items go to backlog
                        completed_at=None,
                        source_sprint_id_for_action_item=None,
                    )

                    self.db.add(work_item)
                    # Transaction commits automatically at end of async with block

                # Refresh to get updated timestamps
                await self.db.refresh(work_item)
                return WorkItemResponse.model_validate(work_item)

            except Exception as e:
                # Handle database constraint violations or race conditions
                if attempt == max_retries - 1:
                    if "connection" in str(e).lower():
                        raise DatabaseError.connection_error() from e
                    elif "constraint" in str(e).lower():
                        raise DatabaseError.constraint_violation(str(e)) from e
                    else:
                        raise DatabaseError.priority_calculation_failed(
                            max_retries
                        ) from e
                # Retry for race conditions
                continue

        # This should never be reached, but satisfy type checker
        raise DatabaseError.priority_calculation_failed(max_retries)

    async def update_work_item(
        self,
        work_item_id: uuid.UUID,
        work_item_data: WorkItemUpdateRequest,
        user_id: uuid.UUID,
    ) -> WorkItemResponse:
        """
        Update an existing work item.

        Args:
            work_item_id: ID of work item to update
            work_item_data: Updated work item data
            user_id: ID of user making the update

        Returns:
            WorkItemResponse: Updated work item

        Raises:
            ValueError: If work item not found or user not authorized
        """
        # Get existing work item
        query = select(WorkItem).where(WorkItem.id == work_item_id)
        result = await self.db.execute(query)
        work_item = result.scalar_one_or_none()

        if not work_item:
            raise ValueError("Work item not found")

        # Verify user is team member
        if not await self._is_team_member(work_item.team_id, user_id):
            raise ValueError("User is not a member of this team")

        # Update fields
        update_data = work_item_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(work_item, field, value)

        await self.db.commit()
        await self.db.refresh(work_item)

        return WorkItemResponse.model_validate(work_item)

    async def delete_work_item(
        self,
        work_item_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """
        Soft delete a work item (mark as archived).

        Args:
            work_item_id: ID of work item to delete
            user_id: ID of user making the deletion

        Returns:
            bool: True if deleted successfully

        Raises:
            ValueError: If work item not found or user not authorized
        """
        # Get existing work item
        query = select(WorkItem).where(WorkItem.id == work_item_id)
        result = await self.db.execute(query)
        work_item = result.scalar_one_or_none()

        if not work_item:
            raise ValueError("Work item not found")

        # Verify user is team member
        if not await self._is_team_member(work_item.team_id, user_id):
            raise ValueError("User is not a member of this team")

        # Soft delete (mark as archived)
        work_item.status = WorkItemStatus.ARCHIVED
        await self.db.commit()

        return True

    async def archive_work_item(
        self,
        work_item_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> WorkItemResponse:
        """
        Archive a work item (soft delete by setting status to archived).

        This method implements Story 2.5 requirements:
        - Updates status to 'archived' instead of permanent deletion
        - Maintains all relationships and data integrity
        - Provides team membership authorization
        - Returns updated work item for optimistic UI updates

        Args:
            work_item_id: ID of work item to archive
            user_id: ID of user making the archival

        Returns:
            WorkItemResponse: Updated work item with 'archived' status

        Raises:
            ValueError: If work item not found or user not authorized
        """
        # Get existing work item
        query = select(WorkItem).where(WorkItem.id == work_item_id)
        result = await self.db.execute(query)
        work_item = result.scalar_one_or_none()

        if not work_item:
            raise ValueError("Work item not found")

        # Verify user is team member
        if not await self._is_team_member(work_item.team_id, user_id):
            raise ValueError("User is not a member of this team")

        # Archive work item (soft delete)
        work_item.status = WorkItemStatus.ARCHIVED
        await self.db.commit()
        await self.db.refresh(work_item)

        return WorkItemResponse.model_validate(work_item)

    async def update_work_item_priority(
        self,
        work_item_id: uuid.UUID,
        priority_data,  # PriorityUpdateRequest - import added below
        user_id: uuid.UUID,
    ) -> WorkItemResponse:
        """
        Update work item priority based on the specified action.

        This method implements Story 2.6 requirements:
        - Handles move_to_top, move_up, move_down, move_to_bottom actions
        - Implements conflict detection for concurrent changes
        - Uses atomic transactions for priority recalculation
        - Provides proper error handling for edge cases

        Args:
            work_item_id: ID of work item to update
            priority_data: Priority update request with action
            user_id: ID of user making the update

        Returns:
            WorkItemResponse: Updated work item with new priority

        Raises:
            ValueError: If work item not found or user not authorized
            HTTPException: 409 if concurrent update conflict detected
            RuntimeError: If priority recalculation fails after retries
        """
        max_retries = 3

        for attempt in range(max_retries):
            try:
                async with self.db.begin():
                    # Get work item with row lock to prevent concurrent updates
                    query = (
                        select(WorkItem)
                        .where(WorkItem.id == work_item_id)
                        .with_for_update()
                    )
                    result = await self.db.execute(query)
                    work_item = result.scalar_one_or_none()

                    if not work_item:
                        raise ValueError("Work item not found")

                    # Verify user is team member
                    if not await self._is_team_member(work_item.team_id, user_id):
                        raise ValueError("User is not a member of this team")

                    # Get current priority-ordered list of team work items (excluding archived)
                    ordered_items_query = (
                        select(WorkItem)
                        .where(
                            and_(
                                WorkItem.team_id == work_item.team_id,
                                WorkItem.status != WorkItemStatus.ARCHIVED,
                            )
                        )
                        .order_by(WorkItem.priority.asc())
                    )
                    result = await self.db.execute(ordered_items_query)
                    ordered_items = result.scalars().all()

                    # Find current position of the work item
                    current_position = None
                    for i, item in enumerate(ordered_items):
                        if item.id == work_item_id:
                            current_position = i
                            break

                    if current_position is None:
                        raise ValueError("Work item not found in team priority list")

                    # Calculate new priority based on action
                    new_priority = await self._calculate_new_priority(
                        priority_data.action,
                        current_position,
                        ordered_items,
                        priority_data.position,
                    )

                    # Handle edge cases with appropriate messages
                    if (
                        priority_data.action == "move_up" and current_position == 0
                    ) or (
                        priority_data.action == "move_to_top" and current_position == 0
                    ):
                        # Item is already at top - no change needed but return success
                        return WorkItemResponse.model_validate(work_item)

                    if (
                        priority_data.action == "move_down"
                        and current_position == len(ordered_items) - 1
                    ) or (
                        priority_data.action == "move_to_bottom"
                        and current_position == len(ordered_items) - 1
                    ):
                        # Item is already at bottom - no change needed but return success
                        return WorkItemResponse.model_validate(work_item)

                    # Update the work item priority
                    work_item.priority = new_priority

                    # Transaction commits automatically at end of async with block

                # Refresh to get updated timestamps
                await self.db.refresh(work_item)
                return WorkItemResponse.model_validate(work_item)

            except Exception as e:
                # Handle database constraint violations or race conditions
                if attempt == max_retries - 1:
                    if "connection" in str(e).lower():
                        raise DatabaseError.connection_error() from e
                    elif (
                        "constraint" in str(e).lower()
                        or "serialization failure" in str(e).lower()
                    ):
                        # Concurrent update detected - return 409 conflict
                        from fastapi import HTTPException, status

                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail={
                                "error": "Priority update conflict",
                                "message": "Another user updated the priority. Please refresh and try again.",
                                "code": "CONCURRENT_UPDATE",
                            },
                        ) from e
                    else:
                        raise RuntimeError(
                            f"Priority update failed after {max_retries} attempts"
                        ) from e
                # Retry for race conditions
                continue

        # This should never be reached, but satisfy type checker
        raise RuntimeError(f"Priority update failed after {max_retries} attempts")

    async def _calculate_new_priority(
        self,
        action: str,
        current_position: int,
        ordered_items: list,
        target_position: Optional[int] = None,
    ) -> float:
        """
        Calculate new priority value based on action and current team priority list.

        Uses priority gaps strategy to minimize cascading updates:
        - Uses gaps of 1000 between items when possible
        - Falls back to midpoint calculation when gaps are small

        Args:
            action: Priority action (move_to_top, move_up, etc.)
            current_position: Current 0-based position in ordered list
            ordered_items: List of work items ordered by priority
            target_position: Target position for SET_POSITION (1-based)

        Returns:
            float: New priority value
        """
        if action == "move_to_top":
            if len(ordered_items) == 0 or current_position == 0:
                return ordered_items[0].priority if ordered_items else 1000.0
            # Priority lower than current top item
            top_priority = ordered_items[0].priority
            return top_priority - 1000.0

        elif action == "move_to_bottom":
            if len(ordered_items) == 0 or current_position == len(ordered_items) - 1:
                return ordered_items[-1].priority if ordered_items else 1000.0
            # Priority higher than current bottom item
            bottom_priority = ordered_items[-1].priority
            return bottom_priority + 1000.0

        elif action == "move_up":
            if current_position == 0:
                return ordered_items[current_position].priority  # No change
            # Move between current-1 and current position
            prev_item = ordered_items[current_position - 1]
            current_item = ordered_items[current_position]
            return (prev_item.priority + current_item.priority) / 2.0

        elif action == "move_down":
            if current_position == len(ordered_items) - 1:
                return ordered_items[current_position].priority  # No change
            # Move between current and current+1 position
            current_item = ordered_items[current_position]
            next_item = ordered_items[current_position + 1]
            return (current_item.priority + next_item.priority) / 2.0

        elif action == "set_position" and target_position is not None:
            # Convert 1-based to 0-based position
            target_idx = target_position - 1
            if target_idx < 0:
                target_idx = 0
            elif target_idx >= len(ordered_items):
                target_idx = len(ordered_items) - 1

            if target_idx == 0:
                # Moving to top
                top_priority = ordered_items[0].priority
                return top_priority - 1000.0
            elif target_idx == len(ordered_items) - 1:
                # Moving to bottom
                bottom_priority = ordered_items[-1].priority
                return bottom_priority + 1000.0
            else:
                # Moving to middle position
                prev_item = ordered_items[target_idx - 1]
                next_item = ordered_items[target_idx]
                return (prev_item.priority + next_item.priority) / 2.0

        else:
            raise ValueError(f"Unknown priority action: {action}")

    async def _is_team_member(self, team_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """
        Check if user is a member of the team.

        Args:
            team_id: Team UUID
            user_id: User UUID

        Returns:
            bool: True if user is team member
        """
        query = select(TeamMember).where(
            and_(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def _get_highest_priority(self, team_id: uuid.UUID) -> float:
        """
        Get the highest priority value for work items in a team.
        Uses database-level MAX function for atomicity.

        Args:
            team_id: Team UUID to query

        Returns:
            float: Highest priority value, or 0.0 if no items exist
        """
        query = select(func.max(WorkItem.priority)).where(
            and_(
                WorkItem.team_id == team_id,
                WorkItem.status != WorkItemStatus.ARCHIVED,  # Exclude archived items
            )
        )
        result = await self.db.execute(query)
        max_priority = result.scalar()
        return max_priority if max_priority is not None else 0.0
