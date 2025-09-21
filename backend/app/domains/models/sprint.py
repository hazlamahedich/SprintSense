from datetime import date
from typing import Optional
from uuid import UUID

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domains.models.team import Team  # noqa: F401 - needed for relationship
from app.infra.db import Base


class Sprint(Base):
    __tablename__ = "sprints"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    team_id: Mapped[UUID] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"))
    name: Mapped[str]
    status: Mapped[str] = mapped_column(
        Enum("future", "active", "closed", name="sprint_status"), default="future"
    )
    start_date: Mapped[date]
    end_date: Mapped[date]
    goal: Mapped[Optional[str]]

    # Timestamps automatically handled by triggers
    created_at: Mapped[date]
    updated_at: Mapped[date]

    # Relationships
    team: Mapped[Team] = relationship("Team", back_populates="sprints")
