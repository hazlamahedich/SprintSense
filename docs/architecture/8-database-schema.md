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

## Relationships

- Teams ↔ Team Members (1:Many)
- Users ↔ Team Members (1:Many)
- Teams ↔ Invitations (1:Many)
- Users ↔ Invitations (1:Many via inviter_id)

## Indexes

- Primary key indexes on all id fields
- Foreign key indexes for performance
- Team name indexing for search performance

---
