# SprintSense

[![CI/CD Status](https://github.com/sprintsense/sprintsense/workflows/CI/badge.svg)](https://github.com/sprintsense/sprintsense/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

An open-source, AI-powered agile project management platform designed to enhance sprint planning, execution, and retrospectives through intelligent insights and predictive analytics.

## 🌟 Overview

SprintSense moves beyond traditional project management tools by providing:

- **AI-Powered Backlog Prioritization** - Smart recommendations based on strategic goals
- **Predictive Sprint Planning** - Monte Carlo simulations for realistic capacity planning  
- **Intelligent Retrospectives** - NLP-powered analysis of team feedback
- **Self-Hostable** - Complete control over your data and infrastructure
- **Privacy-First** - End-to-end encryption and GDPR compliance

## 🛠 Tech Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Frontend** | React + TypeScript | 18.2+ | Modern, type-safe UI |
| **UI Library** | Material-UI (MUI) | 5.15+ | Consistent design system |
| **State Management** | Zustand | 4.5+ | Lightweight state management |
| **Backend** | FastAPI + Python | 3.11+ | High-performance API |
| **Database** | PostgreSQL | 16+ | Reliable data persistence |
| **AI/ML** | scikit-learn + spaCy | Latest | Machine learning capabilities |
| **Containerization** | Docker + Compose | Latest | Consistent deployment |
| **Observability** | OpenTelemetry | 1.22+ | Monitoring and tracing |

## 🚀 Getting Started

### Prerequisites

- **Docker & Docker Compose** - For containerized deployment
- **Node.js 20+** - For frontend development  
- **Python 3.11+** - For backend development
- **Poetry** - Python dependency management

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/sprintsense/sprintsense.git
   cd sprintsense
   ```

2. **Start with Docker Compose**
   ```bash
   cd ops
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Development Setup

**Prerequisites for Development**
```bash
# Install pre-commit hooks (required for all contributors)
pip install pre-commit  # or: brew install pre-commit
pre-commit install

# Verify pre-commit setup
pre-commit --version
```

**Backend Development**
```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload
```

**Frontend Development** 
```bash
cd frontend
npm install
npm run dev
```

**Run Tests**
```bash
# Backend tests
cd backend && poetry run pytest

# Frontend tests  
cd frontend && npm run test

# Full pre-commit checks (run this before pushing)
pre-commit run --all-files

# Run ALL quality checks (same as CI pipeline)
./scripts/lint-all.sh
```

## 🏗 Architecture

SprintSense follows a **modular monolith** architecture for the MVP, providing clean separation of concerns while maintaining operational simplicity.

### High-Level Structure

```
sprintsense/
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── api/       # API routes and controllers
│   │   ├── core/      # Configuration and utilities
│   │   ├── domains/   # Business logic modules
│   │   └── infra/     # Database and external services
│   └── tests/         # Backend test suite
├── frontend/          # React application
│   ├── src/
│   │   ├── components/ # Reusable UI components
│   │   ├── pages/     # Page-level components
│   │   ├── services/  # API client and external services
│   │   └── store/     # State management
│   └── tests/         # Frontend test suite
├── ops/               # Infrastructure and deployment
│   └── docker-compose.yml
└── docs/              # Documentation
```

### Key Principles

- **API-First Design** - All functionality exposed through well-documented APIs
- **Progressive Disclosure** - UI complexity managed through contextual interfaces
- **Privacy by Design** - Self-hostable with end-to-end encryption
- **Observability** - Comprehensive logging, metrics, and tracing

## 🔧 CI/CD Pipeline

Our continuous integration and deployment pipeline includes:

- **Code Quality**: ESLint, Prettier, Black, isort
- **Type Safety**: TypeScript, mypy
- **Testing**: Vitest (frontend), pytest (backend)
- **Security**: Dependency scanning, container scanning
- **Documentation**: Automated API docs generation

### Workflow

1. **Pull Request** → Automated CI checks
2. **Main Branch** → Build and deploy to staging
3. **Manual Trigger** → Deploy to development environment
4. **Release Tag** → Deploy to production (future)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`npm test` / `poetry run pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style

- **Frontend**: ESLint + Prettier with TypeScript strict mode
- **Backend**: Black + isort + flake8 + mypy
- **Commits**: Conventional Commits format preferred

## 📈 Roadmap

### Version 0.1 (Current)
- [x] Project initialization and CI/CD
- [x] Basic health monitoring
- [ ] User authentication and team management
- [ ] Basic backlog management

### Version 0.2 (Next)
- [ ] AI-powered backlog prioritization
- [ ] Sprint planning and execution
- [ ] Basic reporting dashboard

### Version 0.3 (Future)
- [ ] Predictive sprint planning
- [ ] AI retrospective analysis
- [ ] Advanced analytics

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Documentation**: [docs/](docs/)
- **API Documentation**: http://localhost:8000/docs (when running)
- **Issues**: [GitHub Issues](https://github.com/sprintsense/sprintsense/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sprintsense/sprintsense/discussions)

## 💡 Why SprintSense?

Traditional project management tools are reactive - they track what happened. SprintSense is **predictive** - it helps you plan what will happen and learn from what did happen.

By combining the power of AI with proven agile methodologies, SprintSense empowers teams to:

- Make data-driven planning decisions
- Identify risks before they become problems  
- Continuously improve through intelligent insights
- Maintain full control over their data and processes

---

Built with ❤️ by the SprintSense team
