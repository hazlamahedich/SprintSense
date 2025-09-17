# SprintSense Development Makefile
# Common tasks for development workflow

.PHONY: help install-hooks check fix test clean backend-test frontend-test backend-format frontend-format

# Colors
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

help: ## Show this help message
	@echo "$(BLUE)SprintSense Development Commands$(NC)"
	@echo "================================"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install-hooks: ## Install and configure all Git hooks
	@echo "$(BLUE)Installing Git hooks...$(NC)"
	chmod +x scripts/install-git-hooks.sh
	./scripts/install-git-hooks.sh
	@echo "$(GREEN)✅ All Git hooks installed$(NC)"

check: ## Run all quality checks (use before committing)
	@echo "$(BLUE)Running pre-commit quality checks...$(NC)"
	chmod +x scripts/pre-commit-checks.sh
	./scripts/pre-commit-checks.sh

fix: ## Automatically fix common formatting and linting issues
	@echo "$(BLUE)Fixing common issues...$(NC)"
	chmod +x scripts/fix-common-issues.sh
	./scripts/fix-common-issues.sh

test: ## Run all tests (backend + frontend)
	@echo "$(BLUE)Running all tests...$(NC)"
	$(MAKE) backend-test
	$(MAKE) frontend-test
	@echo "$(GREEN)✅ All tests completed$(NC)"

backend-test: ## Run backend tests only
	@echo "$(BLUE)Running backend tests...$(NC)"
	cd backend && poetry run pytest tests/ -v

frontend-test: ## Run frontend tests only
	@echo "$(BLUE)Running frontend tests...$(NC)"
	cd frontend && npm run test:run

backend-format: ## Format backend code (Black + isort)
	@echo "$(BLUE)Formatting backend code...$(NC)"
	cd backend && poetry run black app tests migrations
	cd backend && poetry run isort app tests migrations --profile black
	@echo "$(GREEN)✅ Backend formatting completed$(NC)"

frontend-format: ## Format frontend code (Prettier + ESLint)
	@echo "$(BLUE)Formatting frontend code...$(NC)"
	cd frontend && npm run lint:fix
	cd frontend && npm run format
	@echo "$(GREEN)✅ Frontend formatting completed$(NC)"

backend-lint: ## Run backend linting checks
	@echo "$(BLUE)Running backend linting...$(NC)"
	cd backend && poetry run flake8 app tests --max-line-length=88 --extend-ignore=E203,W503
	cd backend && poetry run mypy app --ignore-missing-imports
	@echo "$(GREEN)✅ Backend linting completed$(NC)"

fix-line-lengths: ## Fix line length issues in Python files
	@echo "$(BLUE)Fixing line length issues...$(NC)"
	chmod +x scripts/fix-line-lengths.py
	python3 scripts/fix-line-lengths.py backend/app/**/*.py backend/tests/**/*.py
	@echo "$(GREEN)✅ Line length fixes completed$(NC)"

frontend-lint: ## Run frontend linting checks
	@echo "$(BLUE)Running frontend linting...$(NC)"
	cd frontend && npm run lint
	cd frontend && npm run type-check
	@echo "$(GREEN)✅ Frontend linting completed$(NC)"

backend-deps: ## Install/update backend dependencies
	@echo "$(BLUE)Installing backend dependencies...$(NC)"
	cd backend && poetry install
	@echo "$(GREEN)✅ Backend dependencies installed$(NC)"

frontend-deps: ## Install/update frontend dependencies
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	cd frontend && npm ci
	@echo "$(GREEN)✅ Frontend dependencies installed$(NC)"

deps: ## Install all dependencies
	$(MAKE) backend-deps
	$(MAKE) frontend-deps

dev-backend: ## Start backend development server
	@echo "$(BLUE)Starting backend development server...$(NC)"
	cd backend && poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start frontend development server
	@echo "$(BLUE)Starting frontend development server...$(NC)"
	cd frontend && npm run dev

clean: ## Clean build artifacts and dependencies
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	rm -rf backend/.pytest_cache backend/__pycache__ backend/app/__pycache__
	rm -rf frontend/node_modules/.cache frontend/dist
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)✅ Cleanup completed$(NC)"

pre-commit: fix check ## Fix issues and run checks (recommended before git commit)
	@echo "$(GREEN)✅ Ready for commit!$(NC)"

ci-check: ## Run CI checks locally (mimics GitHub Actions)
	@echo "$(BLUE)Running CI checks locally...$(NC)"
	$(MAKE) deps
	$(MAKE) backend-format
	$(MAKE) frontend-format
	$(MAKE) backend-lint
	$(MAKE) frontend-lint
	$(MAKE) test
	@echo "$(GREEN)✅ All CI checks passed$(NC)"

git-safe: ## Check if repository is in a safe state for push
	@echo "$(BLUE)Checking git repository state...$(NC)"
	@git status --porcelain | grep -q . && echo "$(YELLOW)⚠️  Uncommitted changes detected$(NC)" || echo "$(GREEN)✅ Working directory clean$(NC)"
	@git log --oneline -n 1
	@echo "$(GREEN)✅ Repository ready for operations$(NC)"

automation-status: ## Check automation setup and configuration
	@echo "$(BLUE)Checking automation status...$(NC)"
	chmod +x scripts/automation-status.sh
	./scripts/automation-status.sh

deploy-status: ## Check deployment status and recent deploy commits
	@echo "$(BLUE)Checking deployment status...$(NC)"
	chmod +x scripts/deploy-utils.sh
	./scripts/deploy-utils.sh stats

deploy-commits: ## Show recent deployment commits with changed files
	@echo "$(BLUE)Showing recent deployment commits...$(NC)"
	chmod +x scripts/deploy-utils.sh
	./scripts/deploy-utils.sh commits-and-files 10

deploy-check: ## Check git state and deployment readiness
	@echo "$(BLUE)Checking deployment readiness...$(NC)"
	chmod +x scripts/deploy-utils.sh
	./scripts/deploy-utils.sh check
