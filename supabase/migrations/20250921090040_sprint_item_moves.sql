-- Migration: Create sprint_item_moves table for audit trail
-- Description: Track movement of tasks between sprints and backlog
-- Filename: 20250924_sprint_item_moves.sql

-- Up Migration
BEGIN;

-- Create enum for move types
CREATE TYPE sprint_item_move_type AS ENUM ('backlog', 'next_sprint');

-- Create table for tracking item moves
CREATE TABLE sprint_item_moves (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id),
    from_sprint_id UUID REFERENCES sprints(id),
    to_sprint_id UUID REFERENCES sprints(id),
    moved_to sprint_item_move_type NOT NULL,
    moved_by UUID NOT NULL REFERENCES users(id),
    moved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reason TEXT, -- Optional reason for the move
    CONSTRAINT valid_move CHECK (
        (moved_to = 'backlog' AND to_sprint_id IS NULL) OR
        (moved_to = 'next_sprint' AND to_sprint_id IS NOT NULL)
    )
);

-- Add indices for common queries and foreign key lookups
CREATE INDEX idx_sprint_item_moves_task ON sprint_item_moves(task_id);
CREATE INDEX idx_sprint_item_moves_from_sprint ON sprint_item_moves(from_sprint_id);
CREATE INDEX idx_sprint_item_moves_to_sprint ON sprint_item_moves(to_sprint_id);
CREATE INDEX idx_sprint_item_moves_moved_by ON sprint_item_moves(moved_by);

-- Add index on tasks table for efficient incomplete item queries
CREATE INDEX IF NOT EXISTS idx_tasks_sprint_status ON tasks(sprint_id, status);

-- RLS Policies for audit trail
ALTER TABLE sprint_item_moves ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view moves for tasks in their teams
CREATE POLICY view_moves ON sprint_item_moves
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM tasks t
            JOIN team_members tm ON t.team_id = tm.team_id
            WHERE t.id = sprint_item_moves.task_id
            AND tm.user_id = auth.uid()
        )
    );

-- Policy: Only allow inserts through API (service role)
CREATE POLICY insert_moves ON sprint_item_moves
    FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid() = moved_by);

COMMIT;

-- Down Migration
BEGIN;

DROP TABLE IF EXISTS sprint_item_moves;
DROP TYPE IF EXISTS sprint_item_move_type;
DROP INDEX IF EXISTS idx_tasks_sprint_status;

COMMIT;
