# 4. Data Models

### User (Revised)
**Purpose:** Represents an individual user account in the system. This is the core entity for authentication and identifying who owns or is assigned to various resources.
**Key Attributes:** `id` (UUID), `displayName` (string), `email` (string), `avatarUrl` (string, optional), `password_hash` (string, backend-only), `created_at` (Date), `updated_at` (Date).

### Team (Revised)
**Purpose:** Represents a collection of users who collaborate on projects together. It is the primary container for backlogs, sprints, and other shared resources.
**Key Attributes:** `id` (UUID), `name` (string), `created_at` (Date), `updated_at` (Date).

### TeamMember
**Purpose:** This is a join table entity that connects a `User` to a `Team` and defines their role within that team.
**Key Attributes:** `id` (UUID), `teamId` (FK to Team), `userId` (FK to User), `role` (enum: 'owner', 'member'), `created_at` (Date).

### WorkItem (Revised)
**Purpose:** Represents a single, atomic unit of work in the backlog, such as a user story, bug, or task.
**Key Attributes:** `id` (UUID), `teamId` (FK), `sprintId` (FK, nullable), `authorId` (FK), `assigneeId` (FK, nullable), `type` (enum: 'story', 'bug', 'task'), `title` (string), `description` (string, nullable), `status` (enum: 'backlog', 'todo', 'in_progress', 'done', 'archived'), `priority` (float), `storyPoints` (integer, nullable), `completedAt` (Date, nullable), `created_at` (Date), `updated_at` (Date), `sourceSprintIdForActionItem` (FK, nullable).

### Sprint (Revised)
**Purpose:** Represents a time-boxed iteration (typically 1-4 weeks) during which a committed amount of work is completed.
**Key Attributes:** `id` (UUID), `teamId` (FK), `name` (string), `status` (enum: 'future', 'active', 'closed'), `startDate` (Date), `endDate` (Date), `goal` (string).

### ProjectGoal (Revised)
**Purpose:** Represents a high-level strategic goal for a team, used by the AI Prioritization Service.
**Key Attributes:** `id` (UUID), `teamId` (FK), `description` (string), `priority` (integer), `metric` (string, nullable), `authorId` (FK).

### RetrospectiveFeedback
**Purpose:** Represents a single piece of feedback—a "card"—submitted by a team member during a sprint retrospective.
**Key Attributes:** `id` (UUID), `sprintId` (FK), `authorId` (FK, nullable), `category` (enum: 'went_well', 'did_not_go_well', 'try_next'), `content` (string).

### Invitation
**Purpose:** Represents an invitation for a user to join a team.
**Key Attributes:** `id` (UUID), `teamId` (FK), `email` (string), `role` (enum: 'owner', 'member'), `status` (enum: 'pending', 'accepted', 'declined'), `inviterId` (FK).

---
