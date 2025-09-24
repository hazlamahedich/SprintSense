-- Enable RLS on sprints table
alter table public.sprints enable row level security;

-- Create policies for sprints table
create policy "Team members can view sprints"
  on public.sprints
  for select
  to authenticated
  using (
    auth.uid() in (
      select user_id
      from team_members
      where team_id = sprints.team_id
    )
  );

create policy "Team members can create sprints"
  on public.sprints
  for insert
  to authenticated
  with check (
    auth.uid() in (
      select user_id
      from team_members
      where team_id = sprints.team_id
    )
  );

create policy "Team members can update sprints"
  on public.sprints
  for update
  to authenticated
  using (
    auth.uid() in (
      select user_id
      from team_members
      where team_id = sprints.team_id
    )
  )
  with check (
    auth.uid() in (
      select user_id
      from team_members
      where team_id = sprints.team_id
    )
  );

create policy "Team members can delete sprints"
  on public.sprints
  for delete
  to authenticated
  using (
    auth.uid() in (
      select user_id
      from team_members
      where team_id = sprints.team_id
    )
  );
