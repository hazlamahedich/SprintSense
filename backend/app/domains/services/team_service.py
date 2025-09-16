"""Team service with business logic for team creation and management."""

import uuid
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domains.models.team import Team, TeamMember, TeamRole
from app.domains.models.user import User
from app.domains.schemas.team import TeamCreateRequest, TeamResponse


class TeamService:
    """Service class for team-related business logic."""

    def __init__(self, db_session: AsyncSession) -> None:
        """Initialize the team service with a database session."""
        self.db_session = db_session

    async def get_team_by_id(self, team_id: uuid.UUID) -> Optional[Team]:
        """Get team by ID with members."""
        result = await self.db_session.execute(
            select(Team).options(selectinload(Team.members)).where(Team.id == team_id)
        )
        return result.scalars().first()

    async def get_teams_by_user(self, user_id: uuid.UUID) -> List[Team]:
        """Get all teams where user is a member."""
        result = await self.db_session.execute(
            select(Team)
            .join(TeamMember)
            .where(TeamMember.user_id == user_id)
            .options(selectinload(Team.members))
        )
        return list(result.scalars().all())

    async def check_team_name_exists_for_user(self, name: str, owner_id: uuid.UUID) -> bool:
        """Check if a team with the same name already exists for the user as owner."""
        result = await self.db_session.execute(
            select(Team)
            .join(TeamMember)
            .where(
                and_(
                    Team.name == name,
                    TeamMember.user_id == owner_id,
                    TeamMember.role == TeamRole.OWNER
                )
            )
        )
        existing_team = result.scalars().first()
        return existing_team is not None

    async def create_team(self, team_data: TeamCreateRequest, owner: User) -> TeamResponse:
        """Create a new team with the specified owner.

        Args:
            team_data: Team creation data
            owner: User who will be the team owner

        Returns:
            TeamResponse: The created team data

        Raises:
            ValueError: If team name already exists for this user
        """
        # Check if team name already exists for this user
        if await self.check_team_name_exists_for_user(team_data.name, owner.id):
            raise ValueError(f"Team with name '{team_data.name}' already exists")

        # Create new team instance
        team = Team(name=team_data.name.strip())

        # Add to database
        self.db_session.add(team)
        await self.db_session.flush()  # Flush to get the team ID

        # Create team member record with owner role
        team_member = TeamMember(
            team_id=team.id,
            user_id=owner.id,
            role=TeamRole.OWNER
        )

        self.db_session.add(team_member)
        await self.db_session.commit()
        
        # Refresh to get updated data with relationships
        await self.db_session.refresh(team)
        
        # Load the team with members
        result = await self.db_session.execute(
            select(Team).options(selectinload(Team.members)).where(Team.id == team.id)
        )
        team_with_members = result.scalars().first()

        # Return team data
        return TeamResponse.model_validate(team_with_members)

    async def is_user_team_owner(self, team_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Check if user is the owner of the specified team."""
        result = await self.db_session.execute(
            select(TeamMember).where(
                and_(
                    TeamMember.team_id == team_id,
                    TeamMember.user_id == user_id,
                    TeamMember.role == TeamRole.OWNER
                )
            )
        )
        team_member = result.scalars().first()
        return team_member is not None