"""add feedback reason column

Revision ID: 20250921_feedback
Revises: # previous revision ID will be filled by alembic
Create Date: 2025-09-21 02:53:51.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250921_feedback'
down_revision = '0c438ab6290e'  # Previous migration: add_project_goals_table
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add feedback_reason column to work_items table."""
    op.add_column(
        'work_items',
        sa.Column(
            'feedback_reason',
            sa.String(length=100),
            nullable=True,
            comment='Specific feedback reason for archived recommendations'
        )
    )


def downgrade() -> None:
    """Remove feedback_reason column from work_items table."""
    op.drop_column('work_items', 'feedback_reason')
