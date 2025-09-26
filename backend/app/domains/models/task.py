"""Task domain model."""

from typing import Any, Dict, Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.infra.db import Base


class Task(Base):
    """Task model."""

    __tablename__ = "tasks"

    id = Column(UUID, primary_key=True)
    sprint_id = Column(UUID, ForeignKey("sprints.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), nullable=False, default="todo")
    story_points = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        """Initialize task with given attributes."""
        super().__init__(**kwargs)
