"""Work Item service for business logic operations."""

import uuid
from typing import Optional

from sqlalchemy import and_, desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

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

    async def create_work_item(
        self,
        work_item_data: WorkItemCreateRequest,
        author_id: uuid.UUID,
    ) -> WorkItemResponse:
        """
        Create a new work item.

        Args:
            work_item_data: Work item creation data
            author_id: ID of the user creating the work item

        Returns:
            WorkItemResponse: Created work item

        Raises:
            ValueError: If user is not a team member
        """
        # Verify user is team member
        if not await self._is_team_member(work_item_data.team_id, author_id):
            raise ValueError("User is not a member of this team")

        # Create new work item
        work_item = WorkItem(
            team_id=work_item_data.team_id,
            author_id=author_id,
            assignee_id=work_item_data.assignee_id,
            type=work_item_data.type,
            title=work_item_data.title,
            description=work_item_data.description,
            priority=work_item_data.priority,
            story_points=work_item_data.story_points,
        )

        self.db.add(work_item)
        await self.db.commit()
        await self.db.refresh(work_item)

        return WorkItemResponse.model_validate(work_item)

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
