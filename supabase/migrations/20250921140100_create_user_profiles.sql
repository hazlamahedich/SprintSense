-- Drop existing profiles table and related objects
drop trigger if exists on_auth_user_created on auth.users;
drop function if exists public.handle_new_user();
drop table if exists public.profiles;

-- Create a profiles table that references auth.users
create table public.profiles (
  id uuid not null primary key,
  full_name text,
  email text,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  constraint fk_auth_user
    foreign key (id)
    references auth.users (id)
    on delete cascade
);

-- Enable RLS
alter table public.profiles enable row level security;

-- Create policies
create policy "Public profiles are viewable by authenticated users"
  on public.profiles for select
  using ( auth.role() = 'authenticated' );

create policy "Users can insert their own profile"
  on public.profiles for insert
  with check ( auth.uid() = id );

create policy "Users can update own profile"
  on public.profiles for update
  using ( auth.uid() = id )
  with check ( auth.uid() = id );

-- Create function to handle new user profiles
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
  -- Delete existing profile if any
  delete from public.profiles where id = new.id;
  
  -- Insert new profile
  insert into public.profiles (id, full_name, email)
  values (new.id, new.raw_user_meta_data->>'full_name', new.email);
  return new;
end;
$$;

-- Create trigger for new user profiles
create or replace trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- Initial setup is handled in the auth permissions migration
