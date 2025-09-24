-- Enable required extensions
create extension if not exists "uuid-ossp" schema extensions;
create extension if not exists pgcrypto schema extensions;

-- Create auth schema if not exists
create schema if not exists auth;

-- Grant necessary privileges
grant usage on schema auth to postgres, service_role;
grant all privileges on all tables in schema auth to postgres, service_role;
grant all privileges on all sequences in schema auth to postgres, service_role;
grant all privileges on all routines in schema auth to postgres, service_role;

-- Note: Indexes are created by Supabase automatically

-- Note: RLS policies are managed by Supabase

-- Create trigger function for user management
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
as $$
begin
    insert into public.profiles (id, full_name, email)
    values (
        new.id,
        new.raw_user_meta_data->>'full_name',
        new.email
    );
    return new;
end;
$$;