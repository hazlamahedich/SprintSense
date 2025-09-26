-- Migration: Create tasks table
-- Description: Initialize task management table
-- Filename: 20250921091000_create_tasks_table.sql

BEGIN;

-- Task status enum
CREATE TYPE task_status AS ENUM (
    'To Do',
    'In Progress',
    'Done',
    'Accepted',
    'Blocked'
);

CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id),
    sprint_id UUID REFERENCES sprints(id),
    title TEXT NOT NULL,
    description TEXT,
    status task_status NOT NULL DEFAULT 'To Do',
    points INTEGER DEFAULT 0 CHECK (points >= 0),
    assignee_id UUID REFERENCES users(id),
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS Policy
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY view_team_tasks ON tasks
    FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM team_members tm
            WHERE tm.team_id = tasks.team_id
            AND tm.user_id = auth.uid()
        )
    );

CREATE POLICY create_team_tasks ON tasks
    FOR INSERT
    TO authenticated
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM team_members tm
            WHERE tm.team_id = tasks.team_id
            AND tm.user_id = auth.uid()
        )
    );

CREATE POLICY update_team_tasks ON tasks
    FOR UPDATE
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM team_members tm
            WHERE tm.team_id = tasks.team_id
            AND tm.user_id = auth.uid()
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM team_members tm
            WHERE tm.team_id = tasks.team_id
            AND tm.user_id = auth.uid()
        )
    );

-- Indices
CREATE INDEX idx_tasks_sprint_status ON tasks(sprint_id, status);
CREATE INDEX idx_tasks_team ON tasks(team_id);
CREATE INDEX idx_tasks_assignee ON tasks(assignee_id);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_tasks_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_tasks_updated_at_trigger
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_tasks_updated_at();

COMMIT;
