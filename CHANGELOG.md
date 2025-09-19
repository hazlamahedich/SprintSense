# Changelog

All notable changes to SprintSense will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.1.0] - 2025-01-19

### Added
- **Project Goals Management**: Complete implementation of Story 3.1
  - Strategic goals creation, editing, and deletion with role-based permissions
  - Priority weighting system (1-10 scale) for AI integration readiness
  - Rich text support with character limits and validation
  - Empty state onboarding with AI integration guidance
  - Full audit trail with created_by/updated_by tracking

### Backend
- New `project_goals` table with proper constraints and indexing
- CRUD API endpoints: `/teams/{teamId}/goals` with role-based access control
- Product Owner/Team Owner permissions for goal management
- Team Member read-only access to goals
- Input validation with Pydantic schemas
- Database migration: `0c438ab6290e_add_project_goals_table.py`

### Frontend
- TypeScript interfaces for goal management with role permissions
- Zustand store for goals state management with optimistic updates
- React components for goals list, creation, and editing
- Material-UI integration with custom styling
- Real-time character counting and validation
- Onboarding wizard for first-time goal setup

### Technical Improvements
- Enhanced role-based authorization system
- Improved error handling and logging
- Comprehensive test coverage foundation
- API documentation auto-generation
- Security enhancements with parameterized queries

### Quality Assurance
- **QA Status**: APPROVED (Quality Score: 95/100)
- All 5 acceptance criteria fully validated
- Role permission matrix documented
- AI integration text processing pipeline specified
- Complete requirements traceability maintained

## [0.1.0] - 2025-01-15

### Added
- Initial project setup and architecture
- FastAPI backend with PostgreSQL database
- React frontend with TypeScript and Material-UI
- Docker containerization and CI/CD pipeline
- Health monitoring and basic authentication
- Team management foundation
- Basic work item schema and models

### Infrastructure
- GitHub Actions CI/CD workflows
- Pre-commit hooks with code formatting
- Database migrations with Alembic
- Local development environment setup
- Comprehensive documentation structure

## [Unreleased]

### Planned
- Story 3.2: AI-powered backlog analysis and keyword matching
- Story 3.3: Priority recommendation engine using goals
- Story 3.4: Goal effectiveness scoring and analytics
- Enhanced Supabase integration
- Production deployment pipeline
