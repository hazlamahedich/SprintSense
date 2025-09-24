-- Create team_members table
create table public.team_members (
  id uuid default extensions.uuid_generate_v4() primary key,
  team_id uuid references public.teams(id) on delete cascade not null,
  user_id uuid references auth.users(id) on delete cascade not null,
  role text check (role in ('owner', 'member')) not null default 'member',
  created_at timestamptz default now() not null,
  updated_at timestamptz default now() not null,
  unique(team_id, user_id)
);

-- Set up Row Level Security
alter table public.team_members enable row level security;

-- Create function to add creator as team owner
create or replace function public.handle_team_created()
returns trigger
language plpgsql
security definer
as $$
begin
  insert into public.team_members (team_id, user_id, role)
  values (new.id, auth.uid(), 'owner');
  return new;
end;
$$;

-- Add trigger to automatically add team creator as owner
create trigger on_team_created
  after insert on public.teams
  for each row execute function public.handle_team_created();