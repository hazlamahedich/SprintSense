"""Add sprint velocity tracking

Revision ID: 20250925
Revises: 20250921
Create Date: 2025-09-25 07:38:20.000000

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20250925"
down_revision = "20250921"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add velocity tracking to sprints table
    op.add_column(
        "sprints",
        sa.Column("completed_points", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "sprints",
        sa.Column(
            "velocity_calculated", sa.Boolean(), nullable=False, server_default="false"
        ),
    )
    op.add_column(
        "sprints",
        sa.Column(
            "velocity_calculation_date",
            postgresql.TIMESTAMP(timezone=True),
            nullable=True,
        ),
    )

    # Add index for efficient velocity queries
    op.create_index(
        "idx_sprints_velocity", "sprints", ["team_id", "velocity_calculated"]
    )


def downgrade() -> None:
    # Remove index
    op.drop_index("idx_sprints_velocity")

    # Remove columns
    op.drop_column("sprints", "velocity_calculation_date")
    op.drop_column("sprints", "velocity_calculated")
    op.drop_column("sprints", "completed_points")
