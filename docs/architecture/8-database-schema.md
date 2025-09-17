# 8. Database Schema

The detailed database schema will be implemented via Alembic migration scripts, as defined in the PRD stories. The schema will enforce foreign key constraints and use appropriate indexing for performance.

## Current Tables

### Users Table

- **id** (UUID, Primary Key)
- **email** (String, Unique)
- **display_name** (String)
- **password_hash** (String)
- **avatar_url** (String, Optional)
- **created_at** (DateTime)
- **updated_at** (DateTime)

### Teams Table

- **id** (UUID, Primary Key)
- **name** (String)
- **created_at** (DateTime)
- **updated_at** (DateTime)

### Team Members Table

- **id** (UUID, Primary Key)
- **team_id** (UUID, Foreign Key → teams.id)
- **user_id** (UUID, Foreign Key → users.id)
- **role** (String, Enum: 'owner', 'member')
- **created_at** (DateTime)

### Invitations Table

- **id** (UUID, Primary Key)
- **team_id** (UUID, Foreign Key → teams.id)
- **email** (String)
- **role** (String, Enum: 'owner', 'member')
- **status** (String, Enum: 'pending', 'accepted', 'declined')
- **inviter_id** (UUID, Foreign Key → users.id)
- **created_at** (DateTime)

### Work Items Table

- **id** (UUID, Primary Key)
- **team_id** (UUID, Foreign Key → teams.id)
- **sprint_id** (UUID, nullable, Future FK to sprints.id)
- **author_id** (UUID, Foreign Key → users.id)
- **assignee_id** (UUID, nullable, Foreign Key → users.id)
- **type** (String, Enum: 'story', 'bug', 'task')
- **title** (String, 255 chars)
- **description** (Text, nullable)
- **status** (String, Enum: 'backlog', 'todo', 'in_progress', 'done', 'archived')
- **priority** (Float, default: 0.0)
- **story_points** (Integer, nullable)
- **completed_at** (DateTime, nullable)
- **source_sprint_id_for_action_item** (UUID, nullable, Future FK to sprints.id)
- **created_at** (DateTime)
- **updated_at** (DateTime, nullable)

## Relationships

- Teams ↔ Team Members (1:Many)
- Users ↔ Team Members (1:Many)
- Teams ↔ Invitations (1:Many)
- Users ↔ Invitations (1:Many via inviter_id)
- Teams ↔ Work Items (1:Many)
- Users ↔ Work Items (1:Many via author_id)
- Users ↔ Work Items (1:Many via assignee_id)
- Sprints ↔ Work Items (1:Many, Future implementation)

## Indexes

- Primary key indexes on all id fields
- Foreign key indexes for performance
- Team name indexing for search performance
- Work Items performance indexes:
  - team_id (for team-based queries)
  - status (for filtering by work item status)
  - priority (for ordering and filtering)
  - id (primary key)

---
