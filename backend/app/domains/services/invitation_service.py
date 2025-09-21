"""Invitation service with business logic for invitation management."""

import uuid
from typing import List

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.models.team import Invitation, InvitationStatus, TeamMember
from app.domains.models.user import User
from app.domains.schemas.invitation import (
    InvitationCreateRequest,
    InvitationListItem,
    InvitationResponse,
)


class InvitationService:
    """Service class for invitation-related business logic."""

    def __init__(self, db_session: AsyncSession) -> None:
        """Initialize the invitation service with a database session."""
        self.db_session = db_session

    async def check_user_is_team_member(self, team_id: uuid.UUID, email: str) -> bool:
        """Check if user with email is already a team member."""
        # First get user by email
        user_result = await self.db_session.execute(
            select(User).where(User.email == email)
        )
        user = user_result.scalars().first()

        if not user:
            return False

        # Check if user is a team member
        member_result = await self.db_session.execute(
            select(TeamMember).where(
                and_(
                    TeamMember.team_id == team_id,
                    TeamMember.user_id == user.id,
                )
            )
        )
        team_member = member_result.scalars().first()
        return team_member is not None

    async def check_invitation_exists(self, team_id: uuid.UUID, email: str) -> bool:
        """Check if an active invitation already exists for this email and team."""
        result = await self.db_session.execute(
            select(Invitation).where(
                and_(
                    Invitation.team_id == team_id,
                    Invitation.email == email,
                    Invitation.status == InvitationStatus.PENDING,
                )
            )
        )
        invitation = result.scalars().first()
        return invitation is not None

    async def create_invitation(
        self,
        team_id: uuid.UUID,
        invitation_data: InvitationCreateRequest,
        inviter: User,
    ) -> InvitationResponse:
        """Create a new team invitation.

        Args:
            team_id: UUID of the team to invite to
            invitation_data: Invitation creation data
            inviter: User who is sending the invitation

        Returns:
            InvitationResponse: The created invitation data

        Raises:
            ValueError: If user is already a team member or invitation exists
        """
        # Check if user is already a team member
        if await self.check_user_is_team_member(team_id, invitation_data.email):
            raise ValueError("This user is already a member of this team")

        # Check if invitation already exists
        if await self.check_invitation_exists(team_id, invitation_data.email):
            raise ValueError("An invitation has already been sent to this email")

        # Create new invitation
        invitation = Invitation(
            team_id=team_id,
            email=invitation_data.email.lower(),  # Normalize email
            role=invitation_data.role,
            status=InvitationStatus.PENDING,
            inviter_id=inviter.id,
        )

        # Add to database
        self.db_session.add(invitation)
        await self.db_session.commit()
        await self.db_session.refresh(invitation)

        # Return invitation data
        return InvitationResponse.model_validate(invitation)

    async def get_team_invitations(
        self, team_id: uuid.UUID
    ) -> List[InvitationListItem]:
        """Get all pending invitations for a team with inviter names.

        Args:
            team_id: UUID of the team

        Returns:
            List[InvitationListItem]: List of pending invitations with inviter names
        """
        result = await self.db_session.execute(
            select(Invitation, User.full_name)
            .join(User, Invitation.inviter_id == User.id)
            .where(
                and_(
                    Invitation.team_id == team_id,
                    Invitation.status == InvitationStatus.PENDING,
                )
            )
            .order_by(Invitation.created_at.desc())
        )

        invitations = []
        for invitation, inviter_name in result:
            invitation_item = InvitationListItem(
                id=invitation.id,
                email=invitation.email,
                role=invitation.role,
                status=invitation.status,
                inviter_name=inviter_name,
                created_at=invitation.created_at,
            )
            invitations.append(invitation_item)

        return invitations

    async def get_invitation_by_id(self, invitation_id: uuid.UUID) -> Invitation | None:
        """Get invitation by ID.

        Args:
            invitation_id: UUID of the invitation

        Returns:
            Invitation: The invitation object or None if not found
        """
        result = await self.db_session.execute(
            select(Invitation).where(Invitation.id == invitation_id)
        )
        return result.scalars().first()

