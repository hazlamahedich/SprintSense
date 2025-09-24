"""Project goals service layer."""

from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.models import ProjectGoal


class ProjectGoalService:
    """Service for managing project goals."""

    def __init__(self, db: AsyncSession):
        """Initialize service with database session."""
        self.db = db

    async def get_team_goals(self, team_id: UUID) -> List[ProjectGoal]:
        """Get all goals for a team."""
        result = await self.db.execute(
            select(ProjectGoal).where(ProjectGoal.team_id == team_id)
        )
        return list(result.scalars().all())
