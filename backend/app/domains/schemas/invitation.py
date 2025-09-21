"""Invitation schemas for request/response validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.domains.models.team import InvitationStatus, TeamRole


class InvitationCreateRequest(BaseModel):
    """Request schema for creating an invitation."""

    email: EmailStr = Field(..., description="Email address of the user to invite")
    role: TeamRole = Field(
        default=TeamRole.MEMBER, description="Role for the invited user"
    )


class InvitationResponse(BaseModel):
    """Response schema for invitation details."""

    id: UUID
    team_id: UUID
    email: str
    role: TeamRole
    status: InvitationStatus
    inviter_id: UUID
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class InvitationCreateResponse(BaseModel):
    """Response schema for invitation creation."""

    message: str
    invitation: InvitationResponse


class InvitationListItem(BaseModel):
    """Schema for invitation list item with inviter name."""

    id: UUID
    email: str
    role: TeamRole
    status: InvitationStatus
    inviter_name: str
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class InvitationListResponse(BaseModel):
    """Response schema for invitation list."""

    invitations: list[InvitationListItem]

