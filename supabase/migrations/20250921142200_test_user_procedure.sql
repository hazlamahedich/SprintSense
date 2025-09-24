-- Set proper search path and create function in public schema
set search_path = public, auth, extensions;

create or replace function public.create_test_user(
  p_email text,
  p_password text,
  p_full_name text
) returns uuid
language plpgsql
security definer
set search_path = public, auth, extensions
as $$
declare
  v_user_id uuid;
  v_encrypted_password text;
begin
  -- Generate a new UUID for the user
  v_user_id := gen_random_uuid();
  
  -- Delete existing test user and profile if any
  delete from public.profiles where email = p_email;
  delete from auth.users where email = p_email;
  
  -- Set the correct search path
  set search_path = public, auth, extensions;

  -- Generate encrypted password
  v_encrypted_password := crypt(p_password, gen_salt('bf'));

  -- Create user in auth.users
  insert into auth.users (
    id,
    instance_id,
    email,
    encrypted_password,
    email_confirmed_at,
    created_at,
    updated_at,
    raw_app_meta_data,
    raw_user_meta_data,
    aud,
    role
  )
  values (
    v_user_id,
    '00000000-0000-0000-0000-000000000000',
    p_email,
    v_encrypted_password,
    now(),
    now(),
    now(),
    '{"provider":"email","providers":["email"]}',
    jsonb_build_object('full_name', p_full_name),
    'authenticated',
    'authenticated'
  )
  returning id into v_user_id;

  return v_user_id;
end;
$$;

-- Create a trigger function for profile creation
create or replace function handle_auth_user_created()
returns trigger as $$
begin
  insert into public.profiles (id, email, full_name, created_at, updated_at)
  values (
    new.id,
    new.email,
    coalesce(new.raw_user_meta_data->>'full_name', new.user_metadata->>'full_name'),
    new.created_at,
    new.updated_at
  );
  return new;
end;
$$ language plpgsql security definer;

-- Create the trigger
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row
  execute procedure handle_auth_user_created();

-- Grant execute permission to authenticated users and service_role
GRANT EXECUTE ON FUNCTION public.create_test_user(text, text, text) TO authenticated;
GRANT EXECUTE ON FUNCTION public.create_test_user(text, text, text) TO service_role;
