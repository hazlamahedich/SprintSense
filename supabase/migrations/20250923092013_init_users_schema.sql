-- Create the public.users table
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Add indexes
CREATE INDEX users_email_idx ON public.users(email);

-- Row Level Security policies
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- By default, no one can see users
CREATE POLICY "Users are not visible by default"
    ON public.users
    FOR ALL
    USING (false);

-- Users can see and update their own record
CREATE POLICY "Users can view own record"
    ON public.users
    FOR SELECT
    USING (id = auth.uid());

CREATE POLICY "Users can update own record"
    ON public.users
    FOR UPDATE
    USING (id = auth.uid());

-- Service role can manage users
CREATE POLICY "Service role can manage users"
    ON public.users
    FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');
