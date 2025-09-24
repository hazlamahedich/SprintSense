"""add_project_goals_table

Revision ID: 0c438ab6290e
Revises: ca877e32a459
Create Date: 2025-09-19 20:39:06.488766

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0c438ab6290e"
down_revision: Union[str, Sequence[str], None] = "ca877e32a459"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create the project_goals table
    op.create_table(
        "project_goals",
        sa.Column("id", sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column("team_id", sa.UUID(), nullable=False),
sa.Column("description", sa.String(500), nullable=False),
        sa.Column("priority_weight", sa.Integer(), nullable=False),
        sa.Column("success_metrics", sa.Text(), nullable=True),
        sa.Column("author_id", sa.UUID(), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=False),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"], ondelete="CASCADE"),
sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint('priority_weight >= 1 AND priority_weight <= 10', name='project_goals_priority_weight_range'),
    )

    # Add a unique constraint for (team_id, description) to prevent duplicates
    op.create_unique_constraint('uq_project_goals_team_description', 'project_goals', ['team_id', 'description'])
    op.create_index(
        op.f("ix_project_goals_created_at"),
        "project_goals",
        ["created_at"],
        unique=False,
    )
    op.create_index(op.f("ix_project_goals_id"), "project_goals", ["id"], unique=False)
    op.create_index(
        op.f("ix_project_goals_priority_weight"),
        "project_goals",
        ["priority_weight"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_goals_team_id"), "project_goals", ["team_id"], unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # Drop unique constraint first
    op.drop_constraint('uq_project_goals_team_description', 'project_goals', type_='unique')

    # Drop indexes
    op.drop_index(op.f("ix_project_goals_team_id"), table_name="project_goals")
    op.drop_index(op.f("ix_project_goals_priority_weight"), table_name="project_goals")
    op.drop_index(op.f("ix_project_goals_id"), table_name="project_goals")
    op.drop_index(op.f("ix_project_goals_created_at"), table_name="project_goals")

    # Drop the table
    op.drop_table("project_goals")
    # ### end Alembic commands ###
