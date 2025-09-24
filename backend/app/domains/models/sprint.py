from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from .team import Team

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.db import Base


class SprintStatus(str, Enum):
    """Sprint status values."""

    FUTURE = "future"
    ACTIVE = "active"
    CLOSED = "closed"


class Sprint(Base):
    __tablename__ = "sprints"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    team_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default=SprintStatus.FUTURE,
        nullable=False,
    )
    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    end_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    goal: Mapped[Optional[str]] = mapped_column(
        String(1000),
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

    # Relationships
    team: Mapped["Team"] = relationship("Team", back_populates="sprints")
