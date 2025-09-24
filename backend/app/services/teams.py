"""Team service layer."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.models import TeamMember


class TeamService:
    """Service for managing teams."""

    def __init__(self, db: AsyncSession):
        """Initialize service with database session."""
        self.db = db

    async def is_user_team_member(self, team_id: UUID, user_id: UUID) -> bool:
        """Check if a user is a member of a team."""
        result = await self.db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
            )
        )
        return result.scalar_one_or_none() is not None

    async def is_user_team_owner(self, team_id: UUID, user_id: UUID) -> bool:
        """Check if a user is an owner of a team."""
        result = await self.db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user_id,
                TeamMember.role == "owner",
            )
        )
        return result.scalar_one_or_none() is not None
