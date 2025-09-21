# 4. Technical Assumptions

## Service Architecture: Modular Monolith

  - **Assumption:** For the MVP, we will build a "Modular Monolith" with strong internal boundaries between logical modules (e.g., `planning`, `prediction`, `analytics`).
  - **Rationale:** This provides clean separation of concerns without the high operational overhead of microservices, while allowing for future extraction.

## MVP Stack

  - **Backend:** FastAPI (using Python 3.11)
  - **Frontend:** React 18 (using Node.js 20) with TypeScript
  - **Database:** PostgreSQL 16
  - **AI/ML Pipeline:** Focus on `scikit-learn` and `spaCy` for the MVP.
  - **Asynchronous Tasks:** Use a library-based background task solution like Celery.
  - **Deployment:** Docker & Docker Compose

## Testing Requirements: Pragmatic Testing Strategy

  - **Assumption:** A strong focus on Unit and Integration tests, supplemented by a limited set of critical-path End-to-End (E2E) tests.
  - **Rationale:** This prioritizes development velocity while ensuring a high level of quality for the core logic.

## Frontend Development

  - **Component Development:** We will use **Storybook** to develop and document UI components in isolation.
  - **Rationale:** This will improve developer workflow, increase component reusability, and provide excellent documentation for the design system.
  - **Asset Optimization:** For the MVP, we will rely on the default asset optimization strategies provided by the **Vite** build process (e.g., code splitting, minification).

---
