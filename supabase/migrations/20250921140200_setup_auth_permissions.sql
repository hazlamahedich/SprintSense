-- Enable the supabase_auth schema
create schema if not exists supabase_auth;

-- Set search path for auth schema
set search_path to auth, supabase_auth, public;

-- Set default security settings for auth schema
alter default privileges in schema auth grant all on tables to postgres, service_role;

-- Enable auth for the service role
grant usage on schema auth to service_role;
grant all on all tables in schema auth to service_role;

-- Add auth extensions if not present
create extension if not exists "uuid-ossp" schema extensions;
create extension if not exists pgcrypto schema extensions;

-- Enable auth for postgres to manage test users
grant usage on schema auth to postgres;
grant all on all tables in schema auth to postgres;
grant all on all sequences in schema auth to postgres;

-- Enable auth for service_role to handle auth operations
grant usage on schema auth to service_role;
grant all on all tables in schema auth to service_role;
grant all on all sequences in schema auth to service_role;

-- Enable auth for authenticated users
grant usage on schema auth to authenticated;
grant select on all tables in schema auth to authenticated;

-- Enable auth for anon users (needed for login)
grant usage on schema auth to anon;
grant select on all tables in schema auth to anon;

-- Ensure postgres can use required extensions
grant usage on schema extensions to postgres;

-- Test users are created during E2E setup via Supabase auth API
