"""Create sprints table

Revision ID: 20250921_create_sprints_table
Create Date: 2025-09-21 10:20:00.000000
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic
revision = "20250921_create_sprints_table"
down_revision = (
    "ca877e32a459_add_work_items_table"  # Replace with your latest migration ID
)
branch_labels = None
depends_on = None


def upgrade():
    # Create sprint_status enum type
    op.execute(
        """
        CREATE TYPE sprint_status AS ENUM ('future', 'active', 'closed')
        """
    )

    # Create sprints table
    op.create_table(
        "sprints",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "team_id",
            UUID(as_uuid=True),
            sa.ForeignKey("teams.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "status",
            sa.Enum("future", "active", "closed", name="sprint_status"),
            nullable=False,
            default="future",
        ),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("goal", sa.Text),
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
            onupdate=sa.text("now()"),
            nullable=False,
        ),
    )

    # Add constraints
    # 1. Ensure no overlapping sprint dates within the same team
    op.execute(
        """
        CREATE OR REPLACE FUNCTION prevent_overlapping_sprints()
        RETURNS TRIGGER AS $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM sprints
                WHERE team_id = NEW.team_id
                AND id != NEW.id  -- Skip checking against self for updates
                AND (
                    (NEW.start_date BETWEEN start_date AND end_date)
                    OR (NEW.end_date BETWEEN start_date AND end_date)
                    OR (start_date BETWEEN NEW.start_date AND NEW.end_date)
                )
            ) THEN
                RAISE EXCEPTION 'Sprint dates overlap with an existing sprint'
                    USING ERRCODE = 'P0001';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER check_sprint_overlap
        BEFORE INSERT OR UPDATE ON sprints
        FOR EACH ROW
        EXECUTE FUNCTION prevent_overlapping_sprints();
        """
    )

    # 2. Ensure only one active sprint per team
    op.execute(
        """
        CREATE OR REPLACE FUNCTION prevent_multiple_active_sprints()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.status = 'active' AND EXISTS (
                SELECT 1 FROM sprints
                WHERE team_id = NEW.team_id
                AND status = 'active'
                AND id != NEW.id  -- Skip checking against self for updates
            ) THEN
                RAISE EXCEPTION 'Only one sprint can be active per team'
                    USING ERRCODE = 'P0001';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER check_active_sprint
        BEFORE INSERT OR UPDATE ON sprints
        FOR EACH ROW
        EXECUTE FUNCTION prevent_multiple_active_sprints();
        """
    )

    # 3. Validate state transitions
    op.execute(
        """
        CREATE OR REPLACE FUNCTION validate_sprint_state_transition()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Only check if status is being updated
            IF TG_OP = 'UPDATE' AND OLD.status != NEW.status THEN
                -- Validate transitions
                IF OLD.status = 'future' AND NEW.status != 'active' THEN
                    RAISE EXCEPTION 'Invalid sprint state transition: future can only transition to active'
                        USING ERRCODE = 'P0001';
                ELSIF OLD.status = 'active' AND NEW.status != 'closed' THEN
                    RAISE EXCEPTION 'Invalid sprint state transition: active can only transition to closed'
                        USING ERRCODE = 'P0001';
                ELSIF OLD.status = 'closed' THEN
                    RAISE EXCEPTION 'Invalid sprint state transition: closed state cannot transition'
                        USING ERRCODE = 'P0001';
                END IF;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER validate_sprint_transition
        BEFORE UPDATE ON sprints
        FOR EACH ROW
        EXECUTE FUNCTION validate_sprint_state_transition();
        """
    )

    # Create indexes
    op.create_index("ix_sprints_team_id", "sprints", ["team_id"])
    op.create_index("ix_sprints_status", "sprints", ["status"])
    op.create_index("ix_sprints_start_date", "sprints", ["start_date"])
    op.create_index("ix_sprints_end_date", "sprints", ["end_date"])


def downgrade():
    # Drop sprints table and all associated objects
    op.drop_table("sprints")

    # Drop triggers and functions
    op.execute("DROP TRIGGER IF EXISTS check_sprint_overlap ON sprints")
    op.execute("DROP TRIGGER IF EXISTS check_active_sprint ON sprints")
    op.execute("DROP TRIGGER IF EXISTS validate_sprint_transition ON sprints")
    op.execute("DROP FUNCTION IF EXISTS prevent_overlapping_sprints")
    op.execute("DROP FUNCTION IF EXISTS prevent_multiple_active_sprints")
    op.execute("DROP FUNCTION IF EXISTS validate_sprint_state_transition")

    # Drop the enum type
    op.execute("DROP TYPE IF EXISTS sprint_status")
