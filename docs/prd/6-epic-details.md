# 6. Epic Details

## Epic 1: Foundation & User Management

**Expanded Goal:** Establish the project's technical foundation, including a robust database management strategy, and deliver the first piece of tangible user value.

  - **Story 1.1: Project Initialization**
  - As a Developer, I want a new project repository with a basic, well-defined CI/CD pipeline and testing framework, so that we can establish a solid foundation for automated testing and deployment.
  - **AC:** 1. Monorepo created. 2. A basic `README.md` file is created. 3. CI/CD runs linter and unit tests. 4. Manual trigger deploys to dev. 5. `/health` endpoint returns `200 OK`. 6. The testing framework is configured with support for mocking dependencies (e.g., using `unittest.mock`).
  - **Story 1.2: Setup Database Migrations**
  - As a Developer, I want a database migration tool configured for the project, so that we can manage and version our database schema changes safely.
  - **AC:** 1. Alembic is added as a project dependency. 2. Alembic is initialized and configured for the project. 3. The project structure is organized to hold migration scripts.
  - **Story 1.3: Setup API Type Generation**
  - As a Developer, I want an automated way to generate TypeScript types from our backend API specification, so that we can ensure type safety between the frontend and backend.
  - **AC:** 1. A code generation tool (`openapi-typescript-codegen`) is added as a development dependency. 2. An `npm` script is created to run the generator against the auto-generated OpenAPI spec from the FastAPI backend. 3. The generated types are output to the `packages/shared-types` directory. 4. The CI pipeline is updated to include a type-checking step.
  - **Story 1.4: User Registration**
  - As a new user, I want to securely register for an account, so that I can trust the system with my information.
  - **AC:** 1. A new database migration is created for the `users` table. 2. Registration page exists. 3. Handles duplicate emails. 4. Passwords are hashed with `bcrypt`. 5. User created in DB. 6. User logged in and redirected.
  - **Story 1.5: User Login and Logout**
  - As a registered user, I want a secure login and logout process, so that I can be confident my account is protected.
  - **AC:** 1. Login page exists. 2. Handles invalid credentials. 3. Sessions use secure, HTTP-only cookies. 4. Logout invalidates server-side session.
  - **Story 1.6: Team Creation**
  - As a logged-in user, I want to create a new team with a unique name, so that I can organize my work effectively.
  - **AC:** 1. A new database migration is created for the `teams` table. 2. "Create Team" form exists. 3. Handles duplicate team names for the user. 4. Team created in DB with owner. 5. User redirected to team dashboard.
  - **Story 1.7: Invite Users to Team (Placeholder)**
  - As a team owner, I want to be able to invite other users to my team, so that we can prepare for collaboration.
  - **AC:** 1. A new database migration is created for the `invitations` table. 2. "Invite User" feature exists. 3. Handles inviting existing members. 4. Invitation with "pending" status created in DB. 5. Pending invitations are listed.

## Epic 2: Basic Backlog Management

**Expanded Goal:** Provide the core functionality of a product backlog. By the end of this epic, a user will be able to create, view, edit, delete, and manually prioritize work items in a safe, scalable, and collaborative manner.

  - **Story 2.1: Create Work Item Schema**
  - As a Developer, I want to create the database schema for work items, so that we can store backlog data.
  - **AC:** 1. A new database migration is created for the `work_items` and `story_points` tables/fields. 2. The schema is applied to the database.
  - **Story 2.2: View Backlog**
  - As a team member, I want to view the team's backlog efficiently, even if it's very large, so that I can always get a clear overview of our work.
  - **AC:** 1. Backlog page exists. 2. List is paginated or virtualized for performance. 3. Items show title and priority. 4. Handles empty state.
  - **Story 2.3: Create Work Item**
  - As a team member, I want to create a new work item, so that I can add new tasks and ideas.
  - **AC:** 1. "Create" button exists. 2. Form has title (required) and description. 3. New item added to top of backlog. 4. View updates for all users.
  - **Story 2.4: Edit Work Item**
  - As a team member, I want to edit an existing work item, so that I can update its details.
  - **AC:** 1. "Edit" option exists. 2. Shows "user is editing" message to prevent conflicts. 3. Saves and broadcasts updates.
  - **Story 2.5: Soft-Delete Work Item**
  - As a team member, I want to safely delete a work item, so that I can remove irrelevant items without fear of permanent data loss.
  - **AC:** 1. "Delete" option exists. 2. Confirmation dialog shown. 3. Item is marked as "archived" (soft delete). 4. Archived view is out of scope.
  - **Story 2.6: Manual Prioritization**
  - As a team member, I want to manually and accessibly change the priority of work items, so that I can organize the backlog.
  - **AC:** 1. Uses accessible "Move to Top/Up/Down/Bottom" buttons. 2. Saves change. 3. View updates for all users.

## Epic 3: AI-Powered Backlog Prioritization

**Expanded Goal:** Enhance the basic backlog with our first set of AI-powered intelligence to provide data-driven suggestions for prioritization and to help identify related work.

  - **Story 3.1: Manage Project Goals**
  - As a Product Owner, I want to define a simple list of strategic goals for my project, so that the AI can use them as a basis for its recommendations.
  - **AC:** 1. "Goals" section in team settings. 2. User can CRUD text-based goals. 3. Goals stored in DB.
  - **Story 3.2: AI Prioritization Service**
  - As a Developer, I want a backend service that can score work items based on their alignment with our defined project goals, so that we have a foundation for the AI prioritization feature.
  - **AC:** 1. Service/module created. 2. Scores items based on keywords vs. project goals. 3. Exposes endpoint that returns a prioritized list. 4. Unit tested.
  - **Story 3.3: Review and Apply AI Suggestions**
  - As a Product Owner, I want to review the AI's prioritization suggestions one by one and decide whether to accept them, so that I remain in full control of the backlog order.
  - **AC:** 1. "Get AI Suggestion" button exists. 2. AI identifies one high-impact item to move. 3. UI highlights the suggestion with explanation. 4. User can "Accept" or "Reject". 5. "Undo" button appears for 10s after accepting.
  - **Story 3.4: Suggest and Create Epics from Clusters**
  - As a Product Owner, I want the AI to suggest clusters of related items and allow me to create a new epic from them, so that I can more easily organize my backlog.
  - **AC:** 1. "Analyze Backlog" button exists. 2. Backend service identifies clusters. 3. UI displays clusters. 4. User can "Create Epic" from a cluster. 5. Form pre-populates the new epic with clustered items.
  - **Story 3.5: AI-Enhanced Work Item Dependencies** (Added 2025-09-21)
  - As a Product Owner, I want the AI to analyze and suggest work item dependencies based on content similarity and historical patterns, so that I can better understand and manage work item relationships.
  - **AC:** 1. AI service analyzes work item relationships. 2. Dependency suggestions displayed in UI. 3. User can accept/reject suggestions. 4. Performance requirements met. 5. Integration with existing AI features maintained.
  - **Note:** This story was added after initial epic planning. See `/docs/prd/epic-changes.md` for impact analysis and mitigation strategies.

## Epic 4: Sprint Management & Execution

**Expanded Goal:** Provide all the tools necessary to manually manage and execute a sprint, creating a complete, usable workflow from backlog to "Done."

  - **Story 4.1: Add Story Points to Work Items**
  - As a team member, I want to assign story points to a work item, so that we can estimate the effort required.
  - **AC:** 1. "Story Points" field added to work item. 2. User can add/edit value. 3. Value is displayed on cards.
  - **Story 4.2: Sprint Lifecycle Management**
  - As a Product Owner, I want to manage the lifecycle of a sprint with clear rules, so that I can control the flow of work without causing confusion.
  - **AC:** 1. Prevents overlapping sprint dates. 2. "Start Sprint" button is disabled if a sprint is already active. 3. States: Future -> Active -> Closed. 4. UI shows state.
  - **Story 4.3: Assign Work Items to a Future Sprint**
  - As a team member, I want to assign work items to a future sprint, so that we can build our sprint backlog.
  - **AC:** 1. User can assign items to a "Future" sprint. 2. Moves item if already assigned. 3. View updates.
  - **Story 4.4: Active Sprint Board**
  - As a team member, I want an accessible Kanban-style sprint board, so that everyone on the team can track the progress of our work.
  - **AC:** 1. Board for "Active" sprint exists. 2. Columns: To Do, In Progress, Done. 3. Accessible controls (not just drag-drop). 4. Board is screen-reader friendly. 5. Real-time updates.
  - **Story 4.5: Definition of Done**
  - As a team member, I want to mark a work item as "Done," so that we can track our progress and calculate velocity.
  - **AC:** 1. Moving card to "Done" updates status. 2. `completion_date` is recorded. 3. Story points are used for velocity calculation.
  - **Story 4.6: Handle Incomplete Work**
  - As a Product Owner, I want to choose how to handle incomplete work when a sprint ends, so that I can re-prioritize it effectively.
  - **AC:** 1. Dialog on sprint end shows incomplete items. 2. Options: "Move to backlog" or "Move to next sprint". 3. Items are moved based on selection.

## Epic 5: Velocity Tracking & Retrospective Insights

**Expanded Goal:** Introduce the first "learning" features. We will start tracking and visualizing team velocity and build the AI-powered retrospective feature to help teams improve their process.

  - **Story 5.1: Calculate and Display Velocity**
  - As a team member, I want to see our team's velocity, so that we can understand our capacity.
  - **AC:** 1. "Velocity Chart" exists. 2. Shows last 5 sprints. 3. Shows 3-sprint rolling average. 4. Manages expectations for new teams.
  - **Story 5.2: Add Retrospective Feedback**
  - As a team member, I want to add feedback, with the option for it to be anonymous, so that I can be open and honest.
  - **AC:** 1. "Retrospective" tab for "Closed" sprints. 2. Three columns for feedback. 3. "Submit anonymously" checkbox. 4. Anonymous cards show no author.
  - **Story 5.3: AI Retrospective Analysis Service**
  - As a Developer, I want a backend service that analyzes feedback and provides context for its conclusions, so that the insights are transparent.
  - **AC:** 1. Service/module created. 2. Uses NLP for sentiment/topic modeling. 3. Returns summary with themes, sentiment, and contributing card IDs/keywords.
  - **Story 5.4: Display Actionable Retrospective Insights**
  - As a Scrum Master, I want to see the AI's analysis and be able to create action items from it, so that I can guide the team towards concrete improvements.
  - **AC:** 1. "Analyze" button exists. 2. UI shows insights. 3. Themes are interactive. 4. "Create Work Item" button next to each theme.

## Epic 6: AI-Powered Sprint Planning

**Expanded Goal:** Deliver predictive sprint planning by leveraging the historical velocity data to provide teams with a powerful tool to assess the feasibility of their sprint plans.

  - **Story 6.1: AI Sprint Simulation Service**
  - As a Developer, I want a performant backend service that simulates a sprint's outcome, so that we can provide real-time feedback without slowing down the UI.
  - **AC:** 1. Service/module created. 2. Uses performant Monte Carlo simulation. 3. Retrieves historical velocity. 4. Returns probability distribution (25th, 50th, 75th percentiles). 5. Avg response < 500ms.
  - **Story 6.2: Sprint Planning View with AI Simulation**
  - As a Product Owner, I want a sprint planning view with a clear visualization of the AI's prediction, so that I can understand the range of possible outcomes.
  - **AC:** 1. "Plan Sprint" view exists. 2. Includes disclaimer about confidence vs. guarantee. 3. "Run Simulation" button exists. 4. Results shown in histogram/box plot. 5. Highlights 50th/75th percentiles.
  - **Story 6.3: Interactive Simulation**
  - As a Product Owner, I want to add or remove work items and immediately see the impact on the prediction, so that I can fine-tune the plan efficiently.
  - **AC:** 1. User can add/remove items in "Plan Sprint" view. 2. Simulation re-runs automatically on change, with debounce. 3. Visualization updates smoothly.

## Epic 7: Self-Hosting & Deployment

**Expanded Goal:** Fulfill the core promise of providing a clear, documented, and easy-to-use self-hosting option, along with developer documentation, user guides, and operational monitoring.

  - **Story 7.1: Dockerize the Application**
  - As a DevOps Engineer, I want the entire application to be containerized using Docker and Docker Compose, so that it can be deployed consistently.
  - **AC:** 1. `Dockerfile` created. 2. `docker-compose.yml` defines all services. 3. `docker-compose up` starts the app locally. 4. Env vars are documented.
  - **Story 7.2: Create a Configuration File**
  - As a self-hosting user, I want a simple configuration file to manage settings, so that I don't have to edit YAML files directly.
  - **AC:** 1. `docker-compose.yml` uses a `.env` file. 2. File includes DB settings, secrets, etc. 3. `.env.example` file is created and documented.
  - **Story 7.3: Write Self-Hosting Documentation**
  - As a self-hosting user, I want clear, step-by-step documentation, so that I can deploy and manage the application successfully.
  - **AC:** 1. `SELF_HOSTING.md` file created. 2. Includes prerequisites. 3. Provides step-by-step guide. 4. Includes troubleshooting and update sections.
  - **Story 7.4: Document Production Backup Strategy**
  - As a self-hosting user, I want clear documentation on the risks of running a database in Docker and how to properly back it up, so that I don't lose my data.
  - **AC:** 1. The `SELF_HOSTING.md` file is updated with a prominent warning about the risks of running a database in a container in production. 2. The documentation strongly recommends using a managed database service. 3. The documentation provides a clear, step-by-step example of a backup strategy for users who choose to run the database in Docker.
  - **Story 7.5: Create a Deployment Script**
  - As a self-hosting user, I want a simple script to automate the deployment process, so that I can get started as quickly as possible.
  - **AC:** 1. `deploy.sh` script created. 2. Checks prerequisites. 3. Manages `.env` file. 4. Pulls latest images. 5. Starts app with `docker-compose`.
  - **Story 7.6: Generate API Documentation**
  - As a Developer, I want automatically generated, interactive API documentation, so that I can understand and interact with the API endpoints easily.
  - **AC:** 1. The FastAPI application is configured to generate OpenAPI compliant documentation. 2. The documentation is accessible at a standard endpoint (e.g., `/docs`). 3. All API endpoints created in the MVP are included. 4. Models and request/response bodies are clearly documented.
  - **Story 7.7: Create Contribution Guidelines**
  - As an open-source contributor, I want a clear `CONTRIBUTING.md` file, so that I can understand how to set up the project and submit pull requests.
  - **AC:** 1. A `CONTRIBUTING.md` file is created. 2. It includes instructions on setting up the dev environment. 3. It defines the coding standards and the PR process.
  - **Story 7.8: Create Basic User Guide**
  - As a new user, I want a simple, accessible user guide, so that I can quickly understand how to use the core features.
  - **AC:** 1. A `USER_GUIDE.md` file is created. 2. The guide covers the main user journeys. 3. A link to the guide is included in the application's UI.
  - **Story 7.9: Implement Basic Usage Analytics**
  - As a Product Owner, I want basic, anonymous usage analytics, so that we can understand which features are being used and make data-informed product decisions.
  - **AC:** 1. A self-hostable, privacy-focused analytics tool (like PostHog) is chosen. 2. The tool is integrated into the frontend. 3. Basic page views and key events (e.g., "Work Item Created," "Sprint Started") are tracked anonymously.
  - **Story 7.10: Setup Application Monitoring and Logging**
  - As a Developer, I want structured logging and basic application performance monitoring (APM), so that we can diagnose issues and monitor the health of the production system.
  - **AC:** 1. A structured logging library is added to the backend. 2. Logs are written to `stdout`. 3. A basic APM tool (e.g., OpenTelemetry) is integrated. 4. The self-hosting documentation is updated with instructions on how to connect to a logging/monitoring backend.
