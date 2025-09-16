# Testing Strategy

This document outlines the testing strategy for the SprintSense project.

## Guiding Principles

- **Pragmatism:** We favor a pragmatic approach to testing, focusing on delivering the most value for the effort invested.
- **Confidence:** Our tests should give us confidence to refactor and deploy new features.
- **Automation:** We automate as much of the testing process as possible.

## Testing Levels

We employ a mix of testing levels to ensure quality:

- **Unit Tests:** These are the foundation of our testing strategy. They test individual units of code in isolation. We use `pytest` for the backend and `vitest` for the frontend.
- **Integration Tests:** These tests verify that different parts of the system work together as expected. For example, we write integration tests for our API endpoints to ensure they interact correctly with the database.
- **End-to-End (E2E) Tests:** These tests simulate real user scenarios from start to finish. We will have a limited set of critical-path E2E tests to ensure the most important workflows are functioning correctly.

## Frontend Testing

- **Framework:** Vitest
- **Libraries:** React Testing Library
- **Component Tests:** We use Storybook to develop and test UI components in isolation.

## Backend Testing

- **Framework:** Pytest
- **Libraries:** `pytest-asyncio` for asynchronous code, `httpx` for testing API clients.

## Continuous Integration

Our CI pipeline on GitHub Actions runs all tests on every pull request. A pull request cannot be merged unless all tests are passing.
