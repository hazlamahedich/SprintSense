# 🚀 SprintSense Warp Drive Index

## Your comprehensive navigation hub for the SprintSense AI-powered agile project management platform

---

## 📋 Table of Contents

- [🎯 Project Overview](#-project-overview)
- [⚡ Quick Navigation](#-quick-navigation)
- [🏗️ Technical Stack](#️-technical-stack)
- [📁 Directory Structure](#-directory-structure)
- [🔄 Development Workflows](#-development-workflows)
- [📁 Codebase Analysis](#-codebase-analysis-workflow)
- [📚 Documentation Index](#-documentation-index)
- [🚀 Getting Started](#-getting-started)
- [🎭 BMAD Persona Switching](#-bmad-persona-switching)
- [🤖 AI & BMAD Integration](#-ai--bmad-integration)
- [🛠️ Development Tools](#️-development-tools)

---

## 🎯 Project Overview

**SprintSense** is an open-source, AI-powered agile project management platform designed to enhance team collaboration through intelligent automation while prioritizing human agency and data privacy.

### 🎯 Mission

Transform reactive project management into proactive, intelligent workflow optimization for development teams.

### 👥 Target Users

- **Primary:** Development teams (10-50 members) in tech companies
- **Secondary:** Remote-first organizations seeking enhanced collaboration

### 💡 Key Value Propositions

- ✨ **AI-Augmented Sprint Planning** with predictive insights
- 🔒 **Privacy-First Architecture** with self-hosting capabilities
- 🎯 **Smart Backlog Prioritization** using multi-criteria decision analysis
- 🔍 **Intelligent Retrospective Analysis** with pattern recognition
- 📊 **Probabilistic Sprint Forecasting** with Monte Carlo simulations

### 📈 Current Status

- **Phase:** MVP Development (Foundation & Core Features)
- **Version:** Development (Pre-release)
- **Target:** 10 pilot teams within 4 months
- **Goal:** 20% improvement in sprint predictability

---

## ⚡ Quick Navigation

### 🗺️ **Core Documentation**

- [📋 Product Requirements Document](./docs/prd.md) - Complete PRD with epics and user stories
- [🏗️ Architecture Overview](./docs/architecture.md) - Full system architecture documentation
- [📐 Frontend Specification](./docs/front-end-spec.md) - UI/UX guidelines and component specs
- [📝 Project Brief](./docs/brief.md) - Executive summary and project context

### 🛠️ **Development Resources**

- [🤖 BMAD Core Workflows](./.bmad-core/) - AI-assisted development methodology
- [🎨 AI Code Quality Guidelines](./claude_suggestions.md) - Claude optimization strategies
- [📊 Web Bundles](./web-bundles/) - BMAD agent configurations and teams

### 🚀 **Quick Actions**

- **Start Development:** Follow [Getting Started](#-getting-started) guide
- **Review Architecture:** Jump to [Technical Stack](#️-technical-stack)
- **Contribute:** See [Development Workflows](#-development-workflows)
- **AI Assistance:** Check [BMAD Integration](#-ai--bmad-integration)

---

## 🏗️ Technical Stack

### 🎯 **Architecture Pattern**

**Modular Monolith** with strict internal boundaries, deployed via Docker containers

### 💻 **Core Technologies**

| Category | Technology | Version | Purpose |
|----------|------------|---------|---------|
| 🌐 **Frontend** | React | ~19.1.1 | Modern, type-safe UI framework |
| 📝 **Language** | TypeScript | ~5.8.3 | Enhanced type safety and DX |
| 🎨 **UI Library** | Material-UI (MUI) | ~5.18.0 | Comprehensive component system |
| 🎨 **Styling** | Tailwind CSS | Latest | Utility-first CSS framework |
| 🗂️ **State** | Zustand | ~4.5.7 | Lightweight state management |
| 🗄️ **API Client** | Axios | ~1.12.2 | Type-safe API interactions |
| 🛣️ **Routing** | React Router | ~7.9.1 | Client-side routing |
| 📝 **Forms** | React Hook Form + Yup | ~7.62.0 | Form handling and validation |
| 🐍 **Backend** | FastAPI | ~0.109.0 | High-performance API framework |
| 🐍 **Language** | Python | ~3.11-3.14 | Backend runtime |
| 🗄️ **Database** | PostgreSQL | 16.2 | Primary data store |
| ⚡ **Cache** | Redis | 7.2 | Caching & background tasks |
| 🏗️ **Build** | Vite | ~7.1.2 | Next-gen frontend tooling |
| 🚀 **Deployment** | Docker Compose | Latest | Container orchestration |
| 🔍 **Observability** | OpenTelemetry | ~1.22.0 | Distributed tracing |
| 📊 **ML/AI** | scikit-learn, transformers | Latest | ML capabilities |

### 🔧 **Development Tools**

- **Package Manager:** npm workspaces (monorepo)
- **Type Generation:** openapi-typescript-codegen
- **E2E Testing:** Playwright
- **Unit Testing:** Vitest (frontend), pytest (backend)
- **Linting:** ESLint w/ TypeScript, Ruff
- **Formatting:** Prettier, Black, isort
- **Type Checking:** TypeScript strict mode, mypy
- **Pre-commit:** husky (frontend), pre-commit (backend)
- **Monitoring:** OpenTelemetry, structlog
- **CI/CD:** GitHub Actions

### 🎯 **Code Quality Thresholds**

| Metric | Frontend | Backend |
|--------|-----------|----------|
| Test Coverage | 80% | 85% |
| Type Coverage | 95% | 100% |
| Max Complexity | 10 | 8 |
| Max File Size | 400 lines | 500 lines |
| Documentation | TSDoc | Google style docstrings |

### 🏛️ **High-Level Architecture**

```text
┌─────────────────┐    ┌──────────────────────┐
│   React SPA     │────│   FastAPI Backend    │
│  (TypeScript)   │    │     (Python)         │
└─────────────────┘    └──────────┬───────────┘
                                  │
                       ┌──────────┴───────────┐
                       │                      │
                ┌──────▼──────┐    ┌─────────▼─────────┐
                │ PostgreSQL  │    │      Redis        │
                │  Database   │    │ Cache & Queue     │
                └─────────────┘    └───────────────────┘
```

---

## 📁 Directory Structure

```text
SprintSense/
├── 📚 docs/                    # Comprehensive documentation
│   ├── 📋 prd.md              # Product Requirements (sharded)
│   ├── 🏗️ architecture.md     # System architecture (sharded)
│   ├── 📐 front-end-spec.md   # Frontend specifications
│   ├── 📝 brief.md            # Project brief
│   ├── 📁 prd/                # PRD shards by epic
│   └── 📁 architecture/        # Architecture shards
│
├── 🤖 .bmad-core/             # BMAD AI Development Framework
│   ├── 🎭 agents/             # AI agent definitions
│   ├── 📋 tasks/              # BMAD workflow tasks
│   ├── 📊 templates/          # Document templates
│   ├── ✅ checklists/         # Quality gates & checklists
│   ├── 🔄 workflows/          # Greenfield/Brownfield workflows
│   └── 📝 core-config.yaml    # BMAD configuration
│
├── 🌐 .claude/                # Claude AI IDE integration
│   └── 📋 commands/BMad/      # Claude-specific BMAD commands
│
├── 🧠 .gemini/                # Gemini AI IDE integration
│   └── 📋 commands/BMad/      # Gemini-specific BMAD commands
│
├── 📦 web-bundles/            # BMAD agent bundles & configurations
│   ├── 🤖 agents/            # Packaged agent definitions
│   ├── 👥 teams/             # Pre-configured team setups
│   └── 🎯 expansion-packs/   # Specialized domain packs
│
├── 🎨 claude_suggestions.md   # AI code quality guidelines
├── 📄 .roomodes              # Development environment config
└── 🚀 warp.md                # This navigation index
```

### 📂 **Key Directories Explained**

- **📚 `docs/`** - All project documentation with sharded PRD and architecture
- **🤖 `.bmad-core/`** - Core BMAD framework for AI-assisted development
- **📦 `web-bundles/`** - Packaged agent configurations and team templates
- **🎨 `claude_suggestions.md`** - Advanced AI prompting strategies and quality guidelines
- **⚙️ `.roomodes`** - Environment configuration for development tools

---

## 🔄 Development Workflows

### 🤖 **BMAD-Powered Development Cycle**

```text
💡 Idea → 📝 Spec Shard → 👩‍💻 Code Shard → ✅ Quality Gate → 🚀 Deploy
```

1. **💡 Ideation Phase**
   - Use `.bmad-core/tasks/create-next-story.md` for user story generation
   - Leverage AI agents for requirement elicitation
   - Document in PRD shards (`docs/prd/`)

2. **📝 Specification Phase**
   - Generate technical specifications using BMAD templates
   - Update architecture shards as needed
   - Validate with `.bmad-core/checklists/`

3. **👩‍💻 Implementation Phase**
   - Follow `claude_suggestions.md` for AI-assisted coding
   - Use agent teams from `web-bundles/teams/`
   - Maintain coding standards and patterns

4. **✅ Quality Assurance**
   - Execute `.bmad-core/tasks/qa-gate.md` processes
   - Run automated test suites
   - Code review with AI assistance

### 🎯 **AI-Assisted Development Guidelines**

Based on `claude_suggestions.md`:

#### 🏗️ **Architectural Compliance**

- Always reference current system architecture
- Maintain consistent naming conventions
- Include proper error handling and separation of concerns

#### 🎨 **Creative Frontend Development**

- **Forbidden:** Generic blue/white/gray schemes, Bootstrap defaults
- **Required:** Unique color palettes, innovative navigation, custom animations
- **Target:** 8/10+ creativity score for all UI components

#### 🔍 **Quality Validation Pipeline**

1. **Syntax & Standards** - Language compliance, coding standards
2. **Architecture Compliance** - Design patterns, dependency injection
3. **Integration Readiness** - API contracts, database alignment

### 📁 **Codebase Analysis Workflow**

#### 🗜️ **Flatten Codebase Command**

For AI analysis, code reviews, and comprehensive codebase understanding:

```bash
# Basic flatten (all code files)
find . -type f \( -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) \
  -not -path "*/node_modules/*" \
  -not -path "*/.git/*" \
  -not -path "*/dist/*" \
  -not -path "*/build/*" \
  -exec echo "=== {} ===" \; -exec cat {} \; > flattened_codebase.txt

# Flatten with documentation (comprehensive)
find . -type f \( -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" -o -name "*.md" -o -name "*.yaml" -o -name "*.yml" -o -name "*.json" \) \
  -not -path "*/node_modules/*" \
  -not -path "*/.git/*" \
  -not -path "*/dist/*" \
  -not -path "*/build/*" \
  -not -path "*/web-bundles/*" \
  -exec echo "=== {} ===" \; -exec cat {} \; > flattened_full.txt

# Flatten specific subsystem (e.g., BMAD core)
find .bmad-core -type f \( -name "*.md" -o -name "*.yaml" \) \
  -exec echo "=== {} ===" \; -exec cat {} \; > flattened_bmad.txt

# Flatten documentation only
find docs -type f -name "*.md" \
  -exec echo "=== {} ===" \; -exec cat {} \; > flattened_docs.txt
```

#### 🎯 **Use Cases for Flattened Codebase**

1. **🤖 AI Code Review**

   ```bash
   # Generate flattened codebase for AI analysis
   ./scripts/flatten-codebase.sh --type=code --output=ai_review.txt
   # Share ai_review.txt with Claude/GPT for comprehensive review
   ```

2. **📊 Architecture Analysis**

   ```bash
   # Include architecture docs with code
   ./scripts/flatten-codebase.sh --type=full --include-docs --output=arch_analysis.txt
   ```

3. **🔍 Debugging & Troubleshooting**

   ```bash
   # Focus on specific modules
   ./scripts/flatten-codebase.sh --filter="backend|frontend" --output=debug.txt
   ```

4. **📝 Documentation Generation**

   ```bash
   # Extract all documentation for AI-powered doc generation
   ./scripts/flatten-codebase.sh --type=docs --output=doc_source.txt
   ```

#### 🛠️ **Advanced Flatten Script** (Planned)

Create `scripts/flatten-codebase.sh`:

```bash
#!/bin/bash
# Advanced codebase flattening script for SprintSense
# Usage: ./scripts/flatten-codebase.sh [options]

# Options:
# --type=code|docs|full|bmad
# --output=filename.txt
# --filter=regex_pattern
# --exclude=pattern
# --include-tests
# --max-size=MB

# Example usage:
# ./scripts/flatten-codebase.sh --type=code --output=ai_context.txt --max-size=5
```

### ⚡ **Quick Commands**

```bash
# Development setup (planned)
make dev              # Start development environment
make test             # Run test suite
make lint             # Run code linting
make docs             # Generate documentation

# Codebase analysis
make flatten          # Generate flattened codebase for AI
make flatten-docs     # Flatten documentation only
make flatten-code     # Flatten source code only

# BMAD workflows
bmad create-story     # Generate new user story
bmad qa-gate         # Execute quality gate
bmad review-code     # AI-assisted code review
bmad flatten-context  # Generate AI context from codebase
```

---

## 📚 Documentation Index

### 📋 **Product Documentation**

- [📋 Product Requirements Document](./docs/prd.md) - Master PRD
  - [🎯 Goals & Background](./docs/prd/1-goals-and-background-context.md)
  - [📝 Requirements](./docs/prd/2-requirements.md)
  - [🎨 UI Design Goals](./docs/prd/3-user-interface-design-goals.md)
  - [🔧 Technical Assumptions](./docs/prd/4-technical-assumptions.md)
  - [📊 Epic List](./docs/prd/5-epic-list.md)
  - [📖 Epic Details](./docs/prd/6-epic-details.md)
- [📝 Project Brief](./docs/brief.md) - Executive overview

### 🏗️ **Architecture Documentation**

- [🏗️ System Architecture](./docs/architecture.md) - Master architecture
  - [👋 Introduction](./docs/architecture/1-introduction.md)
  - [🔝 High-Level Architecture](./docs/architecture/2-high-level-architecture.md)
  - [💻 Tech Stack](./docs/architecture/3-tech-stack.md)
  - [📊 Data Models](./docs/architecture/4-data-models.md)
  - [🔌 API Specification](./docs/architecture/5-api-specification.md)
  - [🧩 Components](./docs/architecture/6-components.md)
  - [⚡ Core Workflows](./docs/architecture/7-core-workflows.md)
  - [🗄️ Database Schema](./docs/architecture/8-database-schema.md)
  - [🌐 Frontend Architecture](./docs/architecture/9-frontend-architecture.md)
  - [🐍 Backend Architecture](./docs/architecture/10-backend-architecture.md)
  - [📁 Project Structure](./docs/architecture/11-unified-project-structure.md)
  - [🚀 Deployment Architecture](./docs/architecture/12-deployment-architecture.md)

### 🎨 **Frontend Documentation**

- [📐 Frontend Specification](./docs/front-end-spec.md) - UI/UX guidelines

### 🤖 **BMAD Documentation**

<details>
<summary>Click to expand BMAD framework details</summary>

#### 🎭 **Agent Definitions** (`.bmad-core/agents/`)

- `bmad-master.md` - Master orchestrator agent
- `architect.md` - Technical architecture agent
- `po.md` - Product owner agent
- `pm.md` - Project manager agent
- `dev.md` - Developer agent
- `qa.md` - Quality assurance agent
- `analyst.md` - Business analyst agent

#### 📋 **Task Templates** (`.bmad-core/tasks/`)

- `document-project.md` - Project documentation tasks
- `create-next-story.md` - User story generation
- `qa-gate.md` - Quality assurance gates
- `review-story.md` - Story review processes
- `nfr-assess.md` - Non-functional requirements

#### ✅ **Quality Checklists** (`.bmad-core/checklists/`)

- `story-dod-checklist.md` - Definition of done
- `architect-checklist.md` - Architecture review
- `po-master-checklist.md` - Product owner checklist

</details>

### 🎨 **AI Development Guidelines**

- [🤖 Claude Optimization Strategies](./claude_suggestions.md) - Comprehensive AI development guide

---

## 🚀 Getting Started

### 👩‍💻 **Development Workflow**

#### 1. **Initial Setup**

```bash
# Clone and enter project
git clone <repository-url>
cd SprintSense

# Install pre-commit hooks (required)
pip install pre-commit
pre-commit install

# Set up backend
cd backend
poetry install
poetry run alembic upgrade head

# Set up frontend
cd ../frontend
npm install
```

#### 2. **Development Environment**

```bash
# Start local services
cd ops
docker-compose up -d db  # Start PostgreSQL

# Start backend (in backend/)
poetry run uvicorn app.main:app --reload

# Start frontend (in frontend/)
npm run dev

# Generate API types (after backend changes)
npm run gen-types
```

#### 3. **Testing Workflow**

```bash
# Backend tests (in backend/)
poetry run pytest                     # Run all tests
poetry run pytest tests/unit          # Unit tests only
poetry run pytest tests/integration   # Integration tests
poetry run pytest --cov=app          # With coverage

# Frontend tests (in frontend/)
npm run test              # Run unit tests
npm run test:coverage    # With coverage
npm run test:e2e         # Run E2E tests
npm run test:e2e:ui      # E2E with UI
```

#### 4. **Code Quality**

```bash
# Backend quality checks
poetry run black .
      && poetry run isort .
      && poetry run flake8
      && poetry run mypy .

# Frontend quality checks
npm run lint
npm run format
npm run type-check

# Run all checks (root directory)
./scripts/lint-all.sh
```

#### 5. **Branch Workflow**

```bash
# Feature branches
git checkout -b feature/xyz

# Commit with semantic messages
git commit -m "feat(component): add xyz feature"

# After PR approval and QA ✅
git push origin feature/xyz
```

### 📚 **Essential Documentation**

1. [🏗️ Architecture Overview](./docs/architecture.md)
2. [🎨 Frontend Spec](./docs/front-end-spec.md)
3. [📋 Coding Standards](./docs/architecture/coding-standards.md)
4. [✅ Testing Standards](./docs/architecture/testing_standards.md)
5. [🤖 AI Development Guide](./claude_suggestions.md)

### 🔄 **Development Loop**

1. **Story Selection**
   - Review sprint backlog
   - Use BMAD for refinement
   - Check dependencies

2. **Implementation**
   - Follow coding standards
   - Write tests first (TDD)
   - Document as you code
   - Use AI assistance wisely

3. **Quality Gates**
   - Run all tests
   - Check coverage
   - Run linters
   - Update documentation

4. **Review Process**
   - Self-review checklist
   - Peer code review
   - QA verification
   - Documentation review

### 📐 **For Product Managers & Designers**

```bash
# 1. Review product documentation
open docs/brief.md          # Project overview
open docs/prd.md           # Detailed requirements
open docs/front-end-spec.md # UI guidelines

# 2. Understand current epics
open docs/prd/6-epic-details.md

# 3. Use BMAD for story creation
# bmad create-story
```

**🎯 Key Focus Areas:**

- [📋 Goals & Background](./docs/prd/1-goals-and-background-context.md)
- [🎨 UI Design Goals](./docs/prd/3-user-interface-design-goals.md)
- [📊 Epic List](./docs/prd/5-epic-list.md)

### 🤖 **For AI Agents & Assistants**

```bash
# 1. Initialize BMAD framework
cd .bmad-core/
open core-config.yaml

# 2. Review agent configurations
ls agents/               # Available agents
ls tasks/               # Workflow tasks
ls templates/           # Document templates

# 3. Start with project documentation
open tasks/document-project.md
```

**🔧 Configuration:**

- **BMAD Version:** 4.43.1
- **IDE Setup:** Claude, Gemini, Roo integrations
- **Type:** Full installation with expansion packs

---

## 🎭 BMAD Persona Switching

### ⚡ **Quick Persona Activation**

Simply type any of these phrases to instantly switch to the corresponding BMAD agent persona:

| **Command** | **Agent** | **Icon** | **Role** |
|-------------|-----------|----------|----------|
| `switch to dev` | James | 💻 | Full Stack Developer |
| `switch to architect` | Sarah | 🏗️ | Technical Architect |
| `switch to po` | Alex | 📋 | Product Owner |
| `switch to pm` | Morgan | 🎯 | Project Manager |
| `switch to qa` | Jordan | ✅ | Quality Assurance |
| `switch to analyst` | Taylor | 📊 | Business Analyst |
| `switch to sm` | Casey | 🔄 | Scrum Master |
| `switch to ux-expert` | River | 🎨 | UX Expert |
| `switch to bmad-orchestrator` | BMad Orchestrator | 🎭 | Master Orchestrator |

### 🎯 **Persona Activation Process**

When you request a persona switch, the AI will:

1. **🔄 Load Agent Configuration** - Read the specific agent file from `.bmad-core/agents/`
2. **⚙️ Initialize Core Settings** - Load `core-config.yaml` and required files
3. **🎭 Adopt Identity** - Transform into the agent's personality and role
4. **📋 Display Commands** - Automatically show `*help` with available commands
5. **⏸️ Await Instructions** - Ready to execute agent-specific workflows

### 📋 **Agent-Specific Commands**

Once switched to a persona, all commands use the `*` prefix:

#### 💻 **Dev Agent (James) Commands**

```bash
*help              # Show available commands
*develop-story     # Implement user story tasks sequentially
*explain           # Detailed explanation of recent work
*review-qa         # Apply QA fixes and improvements
*run-tests         # Execute linting and test suites
*exit              # Exit persona and return to general mode
```

#### 🏗️ **Architect Agent (Sarah) Commands**

```bash
*help              # Show available commands
*review-architecture  # Analyze current architecture
*create-design     # Generate technical design documents
*assess-risk       # Evaluate technical risks
*validate-patterns # Check architectural patterns
*exit              # Exit persona and return to general mode
```

#### 📋 **Product Owner (Alex) Commands**

```bash
*help              # Show available commands
*create-story      # Generate new user stories
*prioritize-backlog # Analyze and prioritize features
*review-requirements # Validate business requirements
*stakeholder-sync  # Prepare stakeholder communications
*exit              # Exit persona and return to general mode
```

### 🔄 **Switching Between Personas**

You can switch between personas at any time:

```bash
# From any persona, simply request a switch
"switch to architect"  # Becomes Sarah 🏗️
"switch to dev"        # Becomes James 💻
"switch to qa"         # Becomes Jordan ✅
```

### 🎭 **Master Orchestrator Mode**

Type `switch to bmad-orchestrator` for the ultimate multi-agent experience:

- **🎯 Workflow Coordination** - Manages complex multi-agent tasks
- **🔄 Dynamic Agent Switching** - Automatically switches to best agent for each task
- **📊 Progress Tracking** - Monitors overall project status
- **👥 Team Simulation** - Coordinates multiple agents simultaneously

### ⚙️ **Persona Configuration Files**

Each persona is defined by:

```text
.bmad-core/agents/
├── dev.md                 # 💻 James - Full Stack Developer
├── architect.md           # 🏗️ Sarah - Technical Architect
├── po.md                  # 📋 Alex - Product Owner
├── pm.md                  # 🎯 Morgan - Project Manager
├── qa.md                  # ✅ Jordan - Quality Assurance
├── analyst.md             # 📊 Taylor - Business Analyst
├── sm.md                  # 🔄 Casey - Scrum Master
├── ux-expert.md           # 🎨 River - UX Expert
└── bmad-orchestrator.md   # 🎭 Master Orchestrator
```

### 🚀 **Quick Start Examples**

#### 🔨 **Development Work**

```text
User: "switch to dev"
James: "Hello! I'm James 💻, your Full Stack Developer. *help to see commands."
User: "*develop-story"
James: "Reading current story requirements and implementing tasks..."
```

#### 📋 **Story Creation**

```text
User: "switch to po"
Alex: "Hi! I'm Alex 📋, your Product Owner. *help for my commands."
User: "*create-story"
Alex: "Let me generate a new user story based on our backlog..."
```

#### 🏗️ **Architecture Review**

```text
User: "switch to architect"
Sarah: "Greetings! I'm Sarah 🏗️, your Technical Architect. *help for options."
User: "*review-architecture"
Sarah: "Analyzing current system architecture and identifying improvements..."
```

### 💡 **Pro Tips**

- **🎯 Stay in Character**: Each agent maintains their personality until you switch
- **📋 Use Commands**: All agent commands require the `*` prefix
- **🔄 Switch Freely**: No need to exit before switching to another persona
- **🎭 Orchestrator Power**: Use BMad Orchestrator for complex multi-step workflows
- **📚 Context Aware**: Each agent has access to all project documentation and code

---

## 🤖 AI & BMAD Integration

### 🎯 **BMAD Framework Overview**

**BMAD (Business-Focused, AI-Enhanced Agile Development)** is integrated throughout the project to provide:

- 🤖 **AI Agent Teams** - Specialized agents for different roles
- 📋 **Workflow Automation** - Task templates and checklists
- 🎯 **Quality Gates** - Automated quality assurance
- 📊 **Template Library** - Standardized documentation

### 🎭 **Available Agent Teams**

| Team | Purpose | Configuration |
|------|---------|---------------|
| `team-all.yaml` | Complete development team | All agents active |
| `team-fullstack.yaml` | Full-stack development | Frontend + Backend focus |
| `team-no-ui.yaml` | Backend-only development | API and data focus |
| `team-ide-minimal.yaml` | IDE integration | Lightweight setup |

### 🔄 **Workflow Integration**

```mermaid
graph LR
    A[💡 Idea] --> B[🤖 BMAD Agent]
    B --> C[📝 Spec Generation]
    C --> D[👩‍💻 Code Generation]
    D --> E[✅ Quality Gate]
    E --> F[🚀 Deployment]
```

### 🗜️ **AI Context Generation**

For optimal AI assistance, use the flatten codebase workflow to provide comprehensive context:

```bash
# Generate AI context for code review
make flatten-code && echo "Share flattened_codebase.txt with AI for review"

# Generate full context for architecture discussions
make flatten && echo "Share flattened_full.txt with AI for architecture analysis"

# Generate BMAD context for workflow assistance
find .bmad-core -name "*.md" -exec echo "=== {} ===" \; -exec cat {} \; > bmad_context.txt
```

#### 🎯 **Best Practices for AI Context**

1. **📏 Size Management**
   - Keep flattened files under 5MB for optimal AI processing
   - Use specific filters for focused analysis
   - Split large codebases by subsystem

2. **🏗️ Context Prioritization**
   - Start with architecture and PRD documents
   - Include relevant code sections based on task
   - Add BMAD workflows for process understanding

3. **🔄 Regular Updates**
   - Regenerate context after major changes
   - Update when switching between epics
   - Refresh for new team members or AI sessions

## ✅ **Code Quality Standards**

### 📝 **TypeScript & Frontend Standards**

```typescript
// Type Safety
export interface UserProfile {
  id: string;          // Always use specific types
  email: string;       // No 'any' unless absolutely necessary
  age?: number;        // Optional props marked with '?'
  roles: UserRole[];   // Use enums for fixed values
}

// Component Organization
const UserCard: React.FC<UserProfile> = ({ id, email, age, roles }) => {
  // Props destructured and typed
  const theme = useTheme();  // Hooks at top
  const [isExpanded, setExpanded] = useState(false);

  // Business logic in custom hooks
  const { data, loading } = useUserData(id);

  // JSX follows consistent pattern
  return (
    <Card>
      <CardHeader />
      <CardContent />
      <CardActions />
    </Card>
  );
};
```

#### 📝 **TypeScript Guidelines**

1. **Type Safety**
   - Strict mode enabled
   - No implicit any
   - Exhaustive type checks
   - Proper generics usage

2. **File Organization**
   - One component per file
   - Clear import structure
   - Consistent exports
   - Type definitions separated

3. **Component Patterns**
   - Functional components
   - Props interfaces
   - Custom hooks
   - Proper event types

### 🐍 **Python & Backend Standards**

```python
from typing import Optional, List
from pydantic import BaseModel

class UserProfile(BaseModel):
    """User profile data model.
    
    Attributes:
        id: Unique identifier for the user
        email: User's email address
        age: Optional age of the user
        roles: List of user roles
    """
    id: str
    email: str
    age: Optional[int] = None
    roles: List[str]

    def validate_email(self) -> bool:
        """Validate email format.
        
        Returns:
            bool: True if email is valid
        """
        return '@' in self.email
```

#### 📝 **Python Guidelines**

1. **Type Hints**
   - All functions typed
   - Use typing module
   - Validate with mypy
   - Document complex types

2. **Documentation**
   - Google style docstrings
   - Function purpose
   - Args and returns
   - Usage examples

3. **Code Style**
   - Black formatting
   - isort imports
   - Ruff linting
   - Max line length: 88

### ✅ **Testing Standards**

#### Frontend Tests

```typescript
describe('UserCard', () => {
  it('should render user information', () => {
    const user = mockUserData();
    const { getByText } = render(<UserCard {...user} />);
    expect(getByText(user.email)).toBeInTheDocument();
  });

  it('should handle loading state', () => {
    const { container } = render(<UserCard loading />);
    expect(container).toMatchSnapshot();
  });
});
```

#### Backend Tests

```python
def test_user_profile_validation():
    """Test user profile validation logic."""
    user = UserProfile(
        id="123",
        email="test@example.com",
        roles=["user"]
    )
    assert user.validate_email() is True

@pytest.mark.integration
def test_user_api_create():
    """Integration test for user creation API."""
    response = client.post("/users", json=user_data)
    assert response.status_code == 201
```

### 📋 **Review Process**

#### PR Checklist

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Types checked
- [ ] Lint clean
- [ ] Follows patterns
- [ ] No security issues
- [ ] Performance considered
- [ ] Error handling

#### QA Requirements

1. **Functionality**
   - Core features work
   - Edge cases handled
   - Error states tested
   - Mobile responsive

2. **Performance**
   - Load times < 2s
   - No memory leaks
   - Bundle size optimized
   - DB queries efficient

3. **Security**
   - Input sanitized
   - Auth working
   - Secrets secure
   - CORS configured

### 🔐 **Code Security**

```typescript
// Frontend Security
import { sanitizeHtml } from '../utils';

// Always sanitize user input
const content = sanitizeHtml(userInput);

// Use environment variables
const apiKey = process.env.API_KEY;

// Proper auth headers
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
```

```python
# Backend Security
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

# Always validate input
class UserInput(BaseModel):
    name: str
    email: EmailStr  # Validates email format
    age: conint(ge=0, lt=150)  # Constrains range

# Proper error handling
def get_user(user_id: str) -> User:
    try:
        return db.users.get(user_id)
    except NotFoundError:
        raise HTTPException(status_code=404)
    except DbError:
        raise HTTPException(status_code=500)
```

### 🎨 **AI Quality Standards**

From `claude_suggestions.md`:

#### 🏗️ **Code Generation**

- **Architectural Context** - Always reference system architecture
- **Quality Standards** - Follow established patterns
- **Validation Criteria** - Define acceptance criteria
- **Anti-Patterns** - Avoid common pitfalls

#### 🎨 **Creative Frontend Standards**

- **Minimum Creativity Score:** 8/10
- **Forbidden Patterns:** Generic admin layouts, Bootstrap defaults
- **Required Elements:** Custom animations, unique color palettes
- **Brand Integration:** Reflect product personality

---

## 🛠️ Development Tools

### 🚀 **Build and Deployment Process**

#### 🏗️ **Build Steps**

```bash
# Frontend Build
cd frontend
npm run build            # Production build
npm run build:analyze    # Bundle analysis

# Backend Build
cd ../backend
poetry build            # Package backend

# Container Builds
cd ../ops
docker-compose build    # All services
```

#### 🛠️ **Environment Setup**

```bash
# Development (.env)
ENVIRONMENT=development
LOG_LEVEL=DEBUG
BACKEND_CORS_ORIGINS=http://localhost:5173

# Staging (.env.staging)
ENVIRONMENT=staging
LOG_LEVEL=INFO
BACKEND_CORS_ORIGINS=https://staging.sprintsense.io

# Production (.env.prod)
ENVIRONMENT=production
LOG_LEVEL=WARNING
BACKEND_CORS_ORIGINS=https://sprintsense.io
```

### 📝 **Commit Message Format**

Follow the Conventional Commits specification:

```bash
# Format
<type>(<scope>): <description>
[optional body]
[optional footer(s)]

# Types
feat:     New feature
fix:      Bug fix
docs:     Documentation only
style:    Code style (formatting, missing semi colons, etc)
refactor: Code refactoring
perf:     Performance improvement
test:     Tests
chore:    Tooling, dependencies, etc.

# Examples
git commit -m "feat(auth): add OAuth support"
git commit -m "fix(db): handle connection timeout"
git commit -m "docs(api): update endpoint docs"
```

### 📝 **Deployment Checklist**

1. **Pre-deployment**
   - [ ] All tests passing
   - [ ] Security scan clean
   - [ ] DB migrations ready
   - [ ] Documentation updated
   - [ ] QA approval

2. **Deployment**
   - [ ] Backup database
   - [ ] Apply migrations
   - [ ] Deploy services
   - [ ] Verify health
   - [ ] Smoke tests

3. **Post-deployment**
   - [ ] Monitor errors
   - [ ] Check performance
   - [ ] Verify features
   - [ ] Update status

#### 🔐 **Security Controls**

```bash
# Secrets Management
API_KEY=$(secret_manager --secret-name=name)
api --key=$API_KEY  # Use env vars

# Access Control
- Production deploys need QA sign-off
- Staging restricted to team
- Dev environments isolated
```

### 🔧 **Development Commands**

```bash
# Frontend Development
npm install              # Install dependencies
npm run dev             # Development server
npm run build           # Production build
npm run test            # Test suite
npm run lint            # Code linting

# Backend Development
pip install -r requirements.txt  # Dependencies
python -m uvicorn app:app --reload  # Development server
python -m pytest       # Test suite
python -m ruff check    # Linting

# Docker Development
docker-compose up       # Full stack
docker-compose up db    # Database only
```

### 📊 **Quality Assurance Tools**

- **Testing:** Jest (frontend), Pytest (backend)
- **Linting:** ESLint, Ruff
- **Type Checking:** TypeScript, mypy
- **Code Formatting:** Prettier, Black
- **Pre-commit Hooks:** husky, pre-commit

### 🚀 **Deployment & Infrastructure**

- **Containerization:** Docker + Docker Compose
- **Self-hosting:** Complete setup documentation
- **CI/CD:** GitHub Actions
- **Monitoring:** OpenTelemetry integration
- **Logging:** Structured logging with structlog

---

## 🤝 Contributing

### 📋 **Contribution Workflow**

1. **🍴 Fork & Clone** the repository
2. **📖 Read Documentation** - Start with this `warp.md`
3. **🎯 Choose Epic** - Review [Epic Details](./docs/prd/6-epic-details.md)
4. **🤖 Use BMAD** - Generate stories with `.bmad-core/tasks/`
5. **👩‍💻 Develop** - Follow [AI Guidelines](./claude_suggestions.md)
6. **✅ Quality Gates** - Execute `.bmad-core/checklists/`
7. **🔄 Pull Request** - Submit with AI-generated documentation

### 🎯 **Good First Issues**

Look for issues labeled:

- `good-first-issue` - Beginner-friendly
- `documentation` - Documentation improvements
- `ai-assisted` - AI development opportunities
- `bmad-workflow` - BMAD integration tasks

---

## 🩺 Maintenance and Troubleshooting

### 🔌 Common Issues

- Database connectivity problems
  - Verify Docker db container is healthy: `docker ps` and `docker-compose logs db`
  - Check env vars: POSTGRES_SERVER, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_PORT
  - Test connection from backend: `poetry run python -c "import psycopg, os; print(psycopg.connect(host=os.getenv('POSTGRES_SERVER','localhost'), user='sprintsense', password='sprintsense', dbname='sprintsense'))"`

- Environment setup issues
  - Node version mismatch: use `nvm use 20`
  - Python version mismatch: `pyenv global 3.11`
  - Poetry missing: `brew install poetry`

- Build failures
  - Frontend: clear vite cache `rm -rf node_modules .vite` then `npm ci`
  - Backend: `poetry lock --no-update && poetry install -n`
  - Docker: rebuild `docker-compose build --no-cache`

- Test failures
  - Flaky E2E: use `npm run test:e2e:debug` and retry with `--retries=2`
  - Backend integration: ensure db is seeded; run migrations

### 🚀 Performance Optimization

- Frontend
  - Code-split routes and large components
  - Memoize selectors and components
  - Use `React.Suspense` for async boundaries

- Backend
  - Add DB indexes for frequent queries
  - Use async SQLAlchemy sessions
  - Cache hot paths (Redis)

- Database
  - Analyze queries with `EXPLAIN ANALYZE`
  - Optimize N+1 selects with joins
  - Periodic vacuum and analyze

### 🔄 Update Procedures

- Dependency updates
  - Frontend: `npm outdated` → `npm update` → test → commit
  - Backend: `poetry update` (pin major ranges), run tests

- Schema migrations
  - Create: `alembic revision -m "feat(db): add table xyz"`
  - Apply: `alembic upgrade head`
  - Rollback: `alembic downgrade -1`

- API version management
  - Update OpenAPI via FastAPI
  - Regenerate frontend types: `npm run gen-types`

---

### 🆘 Support & Resources

### 📞 **Getting Help**

- 📖 **Documentation Issues** - Check the [Documentation Index](#-documentation-index)
- 🤖 **AI/BMAD Questions** - Review `.bmad-core/` configurations
- 🐛 **Bugs & Issues** - Create GitHub issue with BMAD-generated context
- 💡 **Feature Requests** - Use BMAD story generation templates

### 🔗 **External Resources**

- **FastAPI Documentation** - <https://fastapi.tiangolo.com/>
- **React Documentation** - <https://react.dev/>
- **Material-UI Documentation** - <https://mui.com/>
- **PostgreSQL Documentation** - <https://www.postgresql.org/docs/>
- **Docker Documentation** - <https://docs.docker.com/>

---

## 🌟 Built with BMAD™ - Business-focused, AI-Enhanced Agile Development

**Last Updated:** September 15, 2025
**BMAD Version:** 4.43.1
**Document Version:** 1.0

---

*Happy coding! 🚀 Let the AI assist, but keep humans in control.*
