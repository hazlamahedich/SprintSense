-- Test data for sprint item moves
-- This file provides test data for E2E testing of sprint completion and item movement

BEGIN;

-- Insert test team
INSERT INTO teams (id, name, created_at)
VALUES (
    'e91e6fe0-5c6a-4f90-a6c7-3342da318b9c',
    'Test Sprint Team',
    NOW()
) ON CONFLICT (id) DO NOTHING;

-- Insert test users
INSERT INTO users (id, email, name, created_at)
VALUES
    ('d2eb28a6-6f90-4c33-8c4a-c529d20b8ce1', 'po@test.com', 'Test PO', NOW()),
    ('1c91e6fe-5c6a-4f90-a6c7-3342da318b9c', 'dev1@test.com', 'Test Dev 1', NOW()),
    ('2c91e6fe-5c6a-4f90-a6c7-3342da318b9c', 'dev2@test.com', 'Test Dev 2', NOW())
ON CONFLICT (id) DO NOTHING;

-- Link users to team
INSERT INTO team_members (team_id, user_id, role, created_at)
VALUES
    ('e91e6fe0-5c6a-4f90-a6c7-3342da318b9c', 'd2eb28a6-6f90-4c33-8c4a-c529d20b8ce1', 'owner', NOW()),
    ('e91e6fe0-5c6a-4f90-a6c7-3342da318b9c', '1c91e6fe-5c6a-4f90-a6c7-3342da318b9c', 'member', NOW()),
    ('e91e6fe0-5c6a-4f90-a6c7-3342da318b9c', '2c91e6fe-5c6a-4f90-a6c7-3342da318b9c', 'member', NOW())
ON CONFLICT (team_id, user_id) DO NOTHING;

-- Insert test sprints (current and next)
INSERT INTO sprints (id, team_id, name, start_date, end_date, status, created_at)
VALUES
    (
        '01234567-89ab-cdef-0123-456789abcdef',
        'e91e6fe0-5c6a-4f90-a6c7-3342da318b9c',
        'Current Sprint',
        NOW() - INTERVAL '13 days',
        NOW() + INTERVAL '1 day',
        'active',
        NOW()
    ),
    (
        '89abcdef-0123-4567-89ab-cdef01234567',
        'e91e6fe0-5c6a-4f90-a6c7-3342da318b9c',
        'Next Sprint',
        NOW() + INTERVAL '2 days',
        NOW() + INTERVAL '16 days',
        'future',
        NOW()
    )
ON CONFLICT (id) DO NOTHING;

-- Insert test tasks with various statuses
INSERT INTO tasks (id, team_id, sprint_id, title, description, status, points, assignee_id, created_by, created_at)
VALUES
    -- Completed tasks (should not appear in incomplete items list)
    (
        'c3d4e5f6-7890-1234-5678-90abcdef1234',
        'e91e6fe0-5c6a-4f90-a6c7-3342da318b9c',
        '01234567-89ab-cdef-0123-456789abcdef',
        'Completed Task 1',
        'This task is done',
        'Done',
        3,
        '1c91e6fe-5c6a-4f90-a6c7-3342da318b9c',
        '1c91e6fe-5c6a-4f90-a6c7-3342da318b9c',
        NOW()
    ),
    (
        'd4e5f6f7-0123-4567-89ab-cdef01234567',
        'e91e6fe0-5c6a-4f90-a6c7-3342da318b9c',
        '01234567-89ab-cdef-0123-456789abcdef',
        'Completed Task 2',
        'This task is also done',
        'Done',
        5,
        '2c91e6fe-5c6a-4f90-a6c7-3342da318b9c',
        '2c91e6fe-5c6a-4f90-a6c7-3342da318b9c',
        NOW()
    ),
    -- Incomplete tasks (should appear in incomplete items list)
    (
        'e5f6f7e8-9012-3456-7890-abcdef123456',
        'e91e6fe0-5c6a-4f90-a6c7-3342da318b9c',
        '01234567-89ab-cdef-0123-456789abcdef',
        'In Progress Task 1',
        'This task is still being worked on',
        'In Progress',
        8,
        '1c91e6fe-5c6a-4f90-a6c7-3342da318b9c',
        '1c91e6fe-5c6a-4f90-a6c7-3342da318b9c',
        NOW()
    ),
    (
        'f6f7e8d9-0123-4567-890a-bcdef1234567',
        'e91e6fe0-5c6a-4f90-a6c7-3342da318b9c',
        '01234567-89ab-cdef-0123-456789abcdef',
        'To Do Task 1',
        'This task has not been started',
        'To Do',
        5,
        '2c91e6fe-5c6a-4f90-a6c7-3342da318b9c',
        '2c91e6fe-5c6a-4f90-a6c7-3342da318b9c',
        NOW()
    ),
    (
        'd7e8f9a0-1234-5678-90ab-cdef12345678',
        'e91e6fe0-5c6a-4f90-a6c7-3342da318b9c',
        '01234567-89ab-cdef-0123-456789abcdef',
        'In Progress Task 2',
        'Another task in progress',
        'In Progress',
        3,
        '1c91e6fe-5c6a-4f90-a6c7-3342da318b9c',
        '1c91e6fe-5c6a-4f90-a6c7-3342da318b9c',
        NOW()
    )
ON CONFLICT (id) DO NOTHING;

-- Reset test sprint_item_moves table (clean slate for tests)
DELETE FROM sprint_item_moves WHERE task_id IN (
    'c3d4e5f6-7890-1234-5678-90abcdef1234',
    'd4e5f6f7-0123-4567-89ab-cdef01234567',
    'e5f6f7e8-9012-3456-7890-abcdef123456',
    'f6f7e8d9-0123-4567-890a-bcdef1234567',
    'd7e8f9a0-1234-5678-90ab-cdef12345678'
);

COMMIT;
