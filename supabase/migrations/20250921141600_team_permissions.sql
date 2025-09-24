-- Enable RLS on teams table
alter table teams enable row level security;

-- Create policies for teams table
create policy "Users can create teams"
  on teams
  for insert
  to authenticated
  with check (true);

create policy "Team members can view their teams"
  on teams
  for select
  to authenticated
  using (
    auth.uid() in (
      select user_id
      from team_members
      where team_id = id
    )
  );

-- Add RLS to team_members table
alter table team_members enable row level security;

-- Create policies for team_members table
create policy "Team members can view team members"
  on team_members
  for select
  to authenticated
  using (
    auth.uid() in (
      select user_id
      from team_members
      where team_id = team_id
    )
  );

create policy "Automatically create team membership for creator"
  on team_members
  for insert
  to authenticated
  with check (user_id = auth.uid());