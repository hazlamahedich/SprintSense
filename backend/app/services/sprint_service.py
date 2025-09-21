from typing import List, Optional
from uuid import UUID

import structlog
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import AsyncCache
from app.domains.models.sprint import Sprint
from app.schemas.sprint import SprintCreate

logger = structlog.get_logger(__name__)


class SprintService:
    def __init__(self):
        self.cache = AsyncCache(ttl_seconds=300)  # 5 minutes TTL

    async def create_sprint(
        self, session: AsyncSession, team_id: UUID, sprint_data: SprintCreate
    ) -> Sprint:
        """
        Create a new sprint.
        Enforces business rules:
        - No overlapping sprint dates within the same team
        - Only one active sprint per team
        """
        try:
            # Create new sprint entity
            sprint = Sprint(
                team_id=team_id,
                name=sprint_data.name,
                status="future",  # All sprints start in future state
                start_date=sprint_data.start_date,
                end_date=sprint_data.end_date,
                goal=sprint_data.goal,
            )

            session.add(sprint)
            await session.commit()
            await session.refresh(sprint)

            # Invalidate team sprints cache
            await self._invalidate_team_cache(team_id)

            return sprint

        except SQLAlchemyError as e:
            # Database constraint violations will be caught here
            error_msg = str(e)
            if "Sprint dates overlap" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Sprint dates overlap with an existing sprint",
                )
            logger.error("Database error creating sprint", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create sprint",
            )

    async def update_sprint_status(
        self, session: AsyncSession, sprint_id: UUID, new_status: str
    ) -> Sprint:
        """
        Update a sprint's status.
        Enforces business rules:
        - Valid state transitions (Future -> Active, Active -> Closed)
        - Only one active sprint per team
        """
        try:
            # Get current sprint
            sprint = await self._get_sprint_by_id(session, sprint_id)
            if not sprint:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Sprint not found"
                )

            # Update status - state transition validations are enforced by database trigger
            sprint.status = new_status
            await session.commit()
            await session.refresh(sprint)

            # Invalidate team sprints cache
            await self._invalidate_team_cache(sprint.team_id)

            return sprint

        except SQLAlchemyError as e:
            error_msg = str(e)
            if "Invalid sprint state transition" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid state transition from {sprint.status} to {new_status}",
                )
            if "Only one sprint can be active" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Another sprint is already active for this team",
                )
            logger.error("Database error updating sprint status", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update sprint status",
            )

    async def list_team_sprints(
        self, session: AsyncSession, team_id: UUID, include_closed: bool = False
    ) -> List[Sprint]:
        """
        Get all sprints for a team, optionally including closed sprints.
        Sprints are ordered by start date.
        """
        cache_key = f"team_sprints:{team_id}:{include_closed}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        try:
            query = select(Sprint).where(Sprint.team_id == team_id)
            if not include_closed:
                query = query.where(Sprint.status != "closed")
            query = query.order_by(Sprint.start_date.asc())

            result = await session.execute(query)
            sprints = result.scalars().all()

            # Cache results
            await self.cache.set(cache_key, sprints)
            return sprints

        except SQLAlchemyError as e:
            logger.error("Database error listing sprints", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to list sprints",
            )

    async def _get_sprint_by_id(
        self, session: AsyncSession, sprint_id: UUID
    ) -> Optional[Sprint]:
        """Get a sprint by ID."""
        query = select(Sprint).where(Sprint.id == sprint_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def _invalidate_team_cache(self, team_id: UUID) -> None:
        """Invalidate all sprint-related caches for a team."""
        pattern = f"team_sprints:{team_id}:*"
        await self.cache.clear_pattern(pattern)
