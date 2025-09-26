"""Work Item domain models."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.db import Base


class WorkItemType(str, Enum):
    """Enum for work item types."""

    STORY = "story"
    BUG = "bug"
    TASK = "task"


class WorkItemStatus(str, Enum):
    """Enum for work item statuses."""

    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    ARCHIVED = "archived"


class WorkItem(Base):
    """WorkItem model representing work items in the backlog."""

    __tablename__ = "work_items"

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
        index=True,
    )
    sprint_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        # Note: Sprint FK constraint will be added in Epic 4
        nullable=True,
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    assignee_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    type: Mapped[WorkItemType] = mapped_column(
        String(20),
        nullable=False,
        default=WorkItemType.STORY,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    status: Mapped[WorkItemStatus] = mapped_column(
        String(20),
        nullable=False,
        default=WorkItemStatus.BACKLOG,
        index=True,
    )
    priority: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        index=True,
    )
    story_points: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    source_sprint_id_for_action_item: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        # Note: Sprint FK constraint will be added in Epic 4
        nullable=True,
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
    feedback_reason: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Specific feedback reason for archived recommendations",
    )

    # Relationships
    team = relationship("Team")
    author = relationship("User", foreign_keys=[author_id])
    assignee = relationship("User", foreign_keys=[assignee_id])

    def __repr__(self) -> str:
        """String representation of WorkItem."""
        return (
            f"<WorkItem(id={self.id}, title='{self.title}', "
            f"type=WorkItemType.{self.type.value.upper()}, "
            f"status=WorkItemStatus.{self.status.value.upper()})>"
        )
