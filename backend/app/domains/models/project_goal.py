"""Project Goal domain model."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.db import Base


class ProjectGoal(Base):
    """ProjectGoal model representing strategic goals for teams.

    This model supports Story 3.1 requirements for AI-powered backlog prioritization
    by storing strategic goals that AI can analyze for work item recommendations.
    """

    __tablename__ = "project_goals"

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
        index=True,  # Performance: queries by team_id are common
    )
    description: Mapped[str] = mapped_column(
        Text,  # Support rich text content up to 500 chars
        nullable=False,
    )
    priority_weight: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,  # Performance: ordering by priority is common
    )
    success_metrics: Mapped[Optional[str]] = mapped_column(
        Text,  # Optional success measurement criteria
        nullable=True,
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,  # Performance: ordering by creation time
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
    )

    # Relationships
    team = relationship("Team", back_populates="project_goals")
    author = relationship("User", foreign_keys=[author_id])
    created_by_user = relationship("User", foreign_keys=[created_by])
    updated_by_user = relationship("User", foreign_keys=[updated_by])

    def __repr__(self) -> str:
        """String representation of ProjectGoal."""
        return (
            f"<ProjectGoal(id={self.id}, team_id={self.team_id}, "
            f"priority_weight={self.priority_weight})>"
        )

