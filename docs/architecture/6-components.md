# 6. Components

### Component Diagram

```mermaid
C4Container
  title "Component Diagram for SprintSense (Detailed)"
  Person(user, "User", "A user of the SprintSense application.")
  System_Boundary(c1, "SprintSense Application (Self-Hosted Docker Environment)") {
    Container(spa, "Frontend App", "React / Vite", "The single-page application that provides the user interface.")
    Container(web_server, "Web Server", "Nginx", "Serves the frontend application and acts as a reverse proxy for the API.")
    Container(api, "Backend Monolith", "FastAPI / Python", "Contains all business logic and AI services.") {
      Component(auth_service, "Auth Service", "Handles user identity and sessions.")
      Component(team_service, "Team Service", "Manages teams and memberships.")
      Component(backlog_service, "Backlog & Sprint Service", "Manages work items and sprints.")
      Component(ai_prio_service, "AI Prioritization Service", "Ranks backlog items.")
      Component(ai_retro_service, "AI Retrospective Service", "Analyzes retrospective feedback.")
      Component(ai_sim_service, "AI Simulation Service", "Forecasts sprint outcomes.")
    }
    ContainerDb(db, "Database", "PostgreSQL", "Stores all primary application data.")
    ContainerDb(cache, "Cache", "Redis", "Used for session storage and background task queuing.")
  }
  Rel(user, web_server, "Uses", "HTTPS")
  Rel(web_server, spa, "Serves static files")
  Rel(spa, web_server, "Makes API calls to /api/*")
  Rel(web_server, api, "Proxies /api/* requests to")
  Rel(api, db, "Reads/Writes")
  Rel(api, cache, "Reads/Writes")
  Rel(backlog_service, team_service, "Uses for authorization")
  Rel(team_service, auth_service, "Uses for user context")
```

### Component List

**1. Web Server (Nginx)**

  - **Responsibility:** Serves the static assets for the React SPA. Acts as a reverse proxy, directing API requests to the backend service.
  - **Dependencies:** Frontend App (files), Backend Monolith (API).
  - **Technology Stack:** Nginx.

**2. Frontend App (React SPA)**

  - **Responsibility:** Renders the UI, manages local UI state.
  - **Dependencies:** Web Server (for API calls).
  - **Technology Stack:** React, MUI, Zustand, Vite.

**3. Backend Monolith (FastAPI)**

  - **Responsibility:** The container for all backend modules.
  - **Dependencies:** Database, Cache.
  - **Technology Stack:** FastAPI, Python.

**4. Auth Service (Internal Module)**

  - **Responsibility:** Manages user identity, registration, login, and sessions.
  - **Dependencies:** Database, Cache.

**5. Team Service (Internal Module)**

  - **Responsibility:** Manages teams and user membership/roles.
  - **Dependencies:** Database, Auth Service.

**6. Backlog & Sprint Service (Internal Module)**

  - **Responsibility:** Manages Work Items and Sprints.
  - **Dependencies:** Database, Team Service (for permissions).

**7. AI Prioritization Service (Internal Module)**

  - **Responsibility:** Ranks backlog items based on project goals.
  - **Dependencies:** Backlog & Sprint Service (to get data).

**8. AI Retrospective Service (Internal Module)**

  - **Responsibility:** Analyzes retrospective feedback for themes and sentiment.
  - **Dependencies:** Backlog & Sprint Service (to get data).

**9. AI Simulation Service (Internal Module)**

  - **Responsibility:** Forecasts sprint outcomes based on historical velocity.
  - **Dependencies:** Backlog & Sprint Service (to get data).

---
