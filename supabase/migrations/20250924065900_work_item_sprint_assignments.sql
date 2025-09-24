-- Migration to add sprint assignments to work items
ALTER TABLE work_items
ADD COLUMN sprint_id UUID REFERENCES sprints(id) ON DELETE SET NULL,
ADD COLUMN version INTEGER NOT NULL DEFAULT 1,
ADD CONSTRAINT valid_sprint_assignment CHECK (
    sprint_id IS NULL OR EXISTS (
        SELECT 1 FROM sprints
        WHERE id = work_items.sprint_id
        AND status = 'Future'
    )
);

-- Create function to handle work item sprint assignments
CREATE OR REPLACE FUNCTION handle_work_item_sprint_assignment()
RETURNS TRIGGER AS $$
BEGIN
    -- Increment version on sprint_id change
    IF OLD.sprint_id IS DISTINCT FROM NEW.sprint_id THEN
        NEW.version = OLD.version + 1;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for work item version management
CREATE TRIGGER work_item_sprint_assignment_trigger
    BEFORE UPDATE OF sprint_id ON work_items
    FOR EACH ROW
    EXECUTE FUNCTION handle_work_item_sprint_assignment();

-- Enable RLS
ALTER TABLE work_items ENABLE ROW LEVEL SECURITY;

-- Create policies for sprint assignments
CREATE POLICY "Team members can assign work items to sprints"
    ON work_items
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM team_members
            WHERE user_id = auth.uid()
            AND team_id = (
                SELECT team_id FROM sprints WHERE id = NEW.sprint_id
            )
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM team_members
            WHERE user_id = auth.uid()
            AND team_id = (
                SELECT team_id FROM sprints WHERE id = NEW.sprint_id
            )
        )
    );

-- Create Realtime configuration for work items
BEGIN;
  -- Drop existing publication if exists
  DROP PUBLICATION IF EXISTS work_items_changes;

  -- Create new publication for work items changes
  CREATE PUBLICATION work_items_changes FOR TABLE work_items;
COMMIT;
