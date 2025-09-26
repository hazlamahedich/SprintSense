-- Create sprint_status enum type
CREATE TYPE sprint_status AS ENUM ('future', 'active', 'closed');

-- Create sprints table
CREATE TABLE sprints (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  team_id UUID REFERENCES teams(id) ON DELETE CASCADE NOT NULL,
  name VARCHAR(255) NOT NULL,
  status sprint_status DEFAULT 'future' NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  goal TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  CONSTRAINT valid_dates CHECK (end_date >= start_date)
);

-- Create indexes for performance
CREATE INDEX idx_sprints_team_id ON sprints(team_id);
CREATE INDEX idx_sprints_status ON sprints(status);

-- Create function to prevent overlapping sprint dates
CREATE OR REPLACE FUNCTION fn_prevent_overlapping_sprints()
  RETURNS trigger AS
$$
BEGIN
  IF EXISTS (
    SELECT 1 FROM sprints s
    WHERE s.team_id = NEW.team_id
    AND s.id != NEW.id -- Allow updating own record
    AND (
      (NEW.start_date BETWEEN s.start_date AND s.end_date)
      OR (NEW.end_date BETWEEN s.start_date AND s.end_date)
      OR (NEW.start_date <= s.start_date AND NEW.end_date >= s.end_date)
    )
  ) THEN
    RAISE EXCEPTION 'Sprint dates overlap with an existing sprint';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to enforce non-overlapping sprints
CREATE TRIGGER tr_prevent_overlapping_sprints
  BEFORE INSERT OR UPDATE ON sprints
  FOR EACH ROW
  EXECUTE FUNCTION fn_prevent_overlapping_sprints();

-- Create function to enforce single active sprint per team
CREATE OR REPLACE FUNCTION fn_enforce_single_active_sprint()
  RETURNS trigger AS
$$
BEGIN
  IF NEW.status = 'active' AND EXISTS (
    SELECT 1 FROM sprints s
    WHERE s.team_id = NEW.team_id
    AND s.status = 'active'
    AND s.id != NEW.id
  ) THEN
    RAISE EXCEPTION 'Only one sprint can be active at a time per team';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to enforce single active sprint
CREATE TRIGGER tr_enforce_single_active_sprint
  BEFORE INSERT OR UPDATE ON sprints
  FOR EACH ROW
  EXECUTE FUNCTION fn_enforce_single_active_sprint();

-- Create function to validate state transitions
CREATE OR REPLACE FUNCTION fn_validate_sprint_state_transition()
  RETURNS trigger AS
$$
BEGIN
  -- Allow any transition during insert
  IF TG_OP = 'INSERT' THEN
    RETURN NEW;
  END IF;

  -- Only allow Future -> Active and Active -> Closed transitions
  IF OLD.status = 'future' AND NEW.status NOT IN ('future', 'active')
    OR OLD.status = 'active' AND NEW.status NOT IN ('active', 'closed')
    OR OLD.status = 'closed' AND NEW.status != 'closed' THEN
    RAISE EXCEPTION 'Invalid sprint state transition from % to %', OLD.status, NEW.status;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to enforce valid state transitions
CREATE TRIGGER tr_validate_sprint_state_transition
  BEFORE UPDATE ON sprints
  FOR EACH ROW
  EXECUTE FUNCTION fn_validate_sprint_state_transition();

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION fn_update_updated_at_column()
  RETURNS trigger AS
$$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic timestamp updates
CREATE TRIGGER tr_sprints_update_timestamp
  BEFORE UPDATE ON sprints
  FOR EACH ROW
  EXECUTE FUNCTION fn_update_updated_at_column();
