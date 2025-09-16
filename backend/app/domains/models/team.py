"""Team domain models."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.db import Base


class TeamRole(str, Enum):
    """Enum for team member roles."""

    OWNER = "owner"
    MEMBER = "member"


class InvitationStatus(str, Enum):
    """Enum for invitation statuses."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"


class Team(Base):
    """Team model representing teams in the system."""

    __tablename__ = "teams"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
    )

    # Relationships
    members = relationship(
        "TeamMember", back_populates="team", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of Team."""
        return f"<Team(id={self.id}, name={self.name})>"


class TeamMember(Base):
    """TeamMember model representing the relationship between users and teams."""

    __tablename__ = "team_members"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[TeamRole] = mapped_column(
        String(20),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    team = relationship("Team", back_populates="members")
    user = relationship("User")

    def __repr__(self) -> str:
        """String representation of TeamMember."""
        return (
            f"<TeamMember(id={self.id}, team_id={self.team_id}, "
            f"user_id={self.user_id}, role={self.role})>"
        )


class Invitation(Base):
    """Invitation model representing team invitations."""

    __tablename__ = "invitations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    role: Mapped[TeamRole] = mapped_column(
        String(20),
        nullable=False,
    )
    status: Mapped[InvitationStatus] = mapped_column(
        String(20),
        nullable=False,
        default=InvitationStatus.PENDING,
    )
    inviter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    team = relationship("Team")
    inviter = relationship("User")

    def __repr__(self) -> str:
        """String representation of Invitation."""
        return (
            f"<Invitation(id={self.id}, team_id={self.team_id}, "
            f"email={self.email}, status={self.status})>"
        )
