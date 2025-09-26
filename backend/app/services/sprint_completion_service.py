"""Sprint completion business logic."""

from __future__ import annotations

from typing import Iterable, List, Optional
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.schemas.sprint_completion import (
    CompleteSprintRequest,
    CompleteSprintResponse,
    IncompleteTaskDto,
    MoveType,
)


class SprintCompletionService:
    """Service to handle sprint completion and incomplete work moves."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_incomplete_items(self, sprint_id: UUID) -> List[IncompleteTaskDto]:
        """Return all items in the sprint that are not done/accepted."""
        # NOTE: Use current domain models
        from app.domains.models import User, WorkItem, WorkItemStatus

        Assignee = aliased(User)

        q = (
            select(
                WorkItem.id,
                WorkItem.title,
                WorkItem.description,
                WorkItem.status,
                WorkItem.story_points.label("points"),
                WorkItem.assignee_id,
                Assignee.full_name.label("assignee_name"),
                WorkItem.created_at,
                WorkItem.updated_at,
            )
            .join(Assignee, Assignee.id == WorkItem.assignee_id, isouter=True)
            .where(
                WorkItem.sprint_id == sprint_id,
                WorkItem.status.notin_(["done", "archived"]),
            )
            .order_by(WorkItem.created_at.asc())
        )
        rows = (await self.db.execute(q)).all()
        return [
            IncompleteTaskDto(
                id=row.id,
                title=row.title,
                description=row.description,
                status=row.status,
                points=row.points or 0,
                assignee_id=row.assignee_id,
                assignee_name=row.assignee_name,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]

    async def complete_sprint(
        self, sprint_id: UUID, request: CompleteSprintRequest, moved_by: UUID
    ) -> CompleteSprintResponse:
        """Complete sprint by moving incomplete items atomically.

        - If action=backlog: set sprint_id=NULL
        - If action=next_sprint: set to_sprint_id to the next planned sprint
        """
        from app.domains.models import Sprint, WorkItem, WorkItemStatus  # type: ignore

        # determine candidate items
        base_criteria = [
            WorkItem.sprint_id == sprint_id,
            WorkItem.status.notin_(["done", "archived"]),
        ]
        if request.item_ids:
            base_criteria.append(WorkItem.id.in_(request.item_ids))

        # determine next sprint if needed
        next_sprint_id: Optional[UUID] = None
        if request.action == MoveType.NEXT_SPRINT:
            next_sprint_id = await self._get_or_create_next_sprint(sprint_id)

        # perform atomic move
        async with self.db.begin():
            # lock target rows to avoid race conditions
            targets = (
                (
                    await self.db.execute(
                        select(WorkItem.id)
                        .where(*base_criteria)
                        .with_for_update(skip_locked=False)
                    )
                )
                .scalars()
                .all()
            )

            if not targets:
                return CompleteSprintResponse(
                    moved_count=0, target=request.action, next_sprint_id=next_sprint_id
                )

            if request.action == MoveType.BACKLOG:
                stmt = (
                    update(WorkItem)
                    .where(WorkItem.id.in_(targets))
                    .values(sprint_id=None)
                )
            else:
                stmt = (
                    update(WorkItem)
                    .where(WorkItem.id.in_(targets))
                    .values(sprint_id=next_sprint_id)
                )

            result = await self.db.execute(stmt)
            moved_count = result.rowcount or 0

            # TODO: insert into audit table sprint_item_moves when ORM mapping exists
            # This can be done via raw SQL INSERT .. SELECT from targets

        return CompleteSprintResponse(
            moved_count=moved_count,
            target=request.action,
            next_sprint_id=next_sprint_id,
        )

    async def _get_or_create_next_sprint(self, current_sprint_id: UUID) -> UUID:
        """Find next planned sprint for the same team, fallback to create one."""
        from app.domains.models import Sprint  # type: ignore

        # Find the current sprint's team
        current_team_id = (
            await self.db.execute(
                select(Sprint.team_id).where(Sprint.id == current_sprint_id)
            )
        ).scalar_one_or_none()
        if current_team_id is None:
            raise ValueError(
                "No next sprint available; please create a planned sprint first."
            )

        # Try to find a planned sprint after now
        next_id = (
            await self.db.execute(
                select(Sprint.id)
                .where(
                    Sprint.team_id == current_team_id,
                    Sprint.status.in_(["planned", "future"]),
                )
                .order_by(Sprint.start_date.asc())
                .limit(1)
            )
        ).scalar_one_or_none()

        if next_id:
            return next_id

        # Create a new planned sprint starting next business day (implementation-specific)
        # For now, we assume there is a process creating sprints ahead of time; raise for clarity
        raise ValueError(
            "No next sprint available; please create a planned sprint first."
        )
