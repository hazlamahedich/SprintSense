# Local Quality Assurance Setup

This document explains how to set up and use local quality assurance tools to catch issues before they reach GitHub.

## Overview

The SprintSense project uses multiple layers of quality assurance to ensure code quality:

1. **Pre-commit hooks** - Automatic checks before each commit
2. **Local scripts** - Manual quality checks and fixes
3. **Makefile commands** - Easy-to-use development workflow
4. **IDE integration** - Real-time feedback during development

## Quick Start

### 1. Install Pre-commit Hooks

```bash
# Install pre-commit (if not already installed)
pip install pre-commit

# Install hooks for this repository
make install-hooks

# Or manually:
pre-commit install
pre-commit install --hook-type pre-push
```

### 2. Basic Workflow

```bash
# Before making changes
make deps                    # Install dependencies

# During development
make fix                     # Fix common issues automatically
make check                   # Run all quality checks

# Before committing
make pre-commit              # Fix + check in one command

# Alternative: use git hooks (automatic)
git add .
git commit -m "your message"  # Hooks run automatically
```

## Available Tools

### Makefile Commands

Run `make help` to see all available commands:

```bash
make help                   # Show all commands
make check                  # Run all quality checks
make fix                    # Auto-fix common issues
make test                   # Run all tests
make pre-commit            # Fix and check (recommended)
make ci-check              # Simulate CI pipeline locally
```

### Manual Scripts

```bash
# Comprehensive quality check
./scripts/pre-commit-checks.sh

# Auto-fix common issues
./scripts/fix-common-issues.sh
```

### Pre-commit Hooks

Automatically run when you commit or push:

- **Code formatting**: Black (Python), Prettier (TypeScript/React)
- **Linting**: Flake8, ESLint, MyPy type checking
- **Tests**: Pytest, Vitest
- **Security**: Bandit security scanning
- **Documentation**: Markdown linting

## Quality Checks Explained

### Backend (Python) Checks

1. **Black Formatting**

   ```bash
   cd backend && poetry run black app tests migrations
   ```

2. **Import Sorting (isort)**

   ```bash
   cd backend && poetry run isort app tests migrations --profile black
   ```

3. **Linting (Flake8)**

   ```bash
   cd backend && poetry run flake8 app tests --max-line-length=88
   ```

4. **Type Checking (MyPy)**

   ```bash
   cd backend && poetry run mypy app --ignore-missing-imports
   ```

5. **Security Scanning (Bandit)**

   ```bash
   cd backend && poetry run bandit -r app
   ```

6. **Tests (Pytest)**

   ```bash
   cd backend && poetry run pytest tests/
   ```

### Frontend (TypeScript/React) Checks

1. **TypeScript Type Checking**

   ```bash
   cd frontend && npm run type-check
   ```

2. **Linting (ESLint)**

   ```bash
   cd frontend && npm run lint
   # Auto-fix: npm run lint:fix
   ```

3. **Formatting (Prettier)**

   ```bash
   cd frontend && npm run format:check
   # Auto-fix: npm run format
   ```

4. **Tests (Vitest)**

   ```bash
   cd frontend && npm run test:run
   ```

## Common Issues and Solutions

### Backend Issues

**Black formatting errors:**

```bash
make backend-format
# Or: cd backend && poetry run black app tests migrations
```

**MyPy type errors:**

```bash
cd backend && poetry run mypy app --ignore-missing-imports
# Fix type annotations in the reported files
```

**Import sorting issues:**

```bash
cd backend && poetry run isort app tests migrations --profile black
```

### Frontend Issues

**ESLint errors:**

```bash
make frontend-format
# Or: cd frontend && npm run lint:fix
```

**TypeScript errors:**

```bash
cd frontend && npm run type-check
# Fix type errors in the reported files
```

**Prettier formatting:**

```bash
cd frontend && npm run format
```

### Git Issues

**Trailing whitespace or line endings:**

```bash
make fix  # Automatically fixes these issues
```

**Large files:**

- Consider using Git LFS for files > 1MB
- Exclude build artifacts in `.gitignore`

## IDE Integration

### VS Code

Install these extensions for real-time quality feedback:

```json
{
  "recommendations": [
    "ms-python.black-formatter",
    "ms-python.flake8",
    "ms-python.mypy-type-checker",
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint",
    "ms-python.isort"
  ]
}
```

Add to `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "./backend/.venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "editor.formatOnSave": true,
  "eslint.workingDirectories": ["frontend"],
  "prettier.workingDirectories": ["frontend"]
}
```

### PyCharm/IntelliJ

1. Configure Black formatter
2. Enable ESLint and Prettier in settings
3. Set up type checking with MyPy
4. Configure auto-format on save

## CI/CD Pipeline Simulation

Run the same checks that GitHub Actions will run:

```bash
make ci-check
```

This runs:

1. Install dependencies
2. Format all code
3. Run all linting checks  
4. Run all tests
5. Verify everything passes

## Troubleshooting

### Poetry Issues

```bash
# Reinstall dependencies
cd backend && rm poetry.lock && poetry install

# Update dependencies
cd backend && poetry update
```

### npm Issues

```bash
# Clean install
cd frontend && rm -rf node_modules package-lock.json && npm install

# Clear cache
cd frontend && npm cache clean --force
```

### Pre-commit Issues

```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Update hooks
pre-commit autoupdate

# Run manually
pre-commit run --all-files
```

## Configuration Files

- **`.pre-commit-config.yaml`** - Pre-commit hook configuration
- **`pyproject.toml`** - Python project and tool configuration
- **`package.json`** - Frontend scripts and dependencies
- **`Makefile`** - Development workflow commands
- **Scripts directory** - Quality check and fix scripts

## Best Practices

1. **Before starting work:**

   ```bash
   make deps          # Ensure dependencies are current
   ```

2. **During development:**

   ```bash
   make fix           # Fix issues as you go
   ```

3. **Before committing:**

   ```bash
   make pre-commit    # Comprehensive check
   ```

4. **Before pushing:**

   ```bash
   make ci-check      # Ensure CI will pass
   ```

5. **Regular maintenance:**

   ```bash
   make clean         # Clean build artifacts
   pre-commit autoupdate  # Update hook versions
   ```

## Performance Tips

- Pre-commit hooks only run on changed files (faster)
- Use `make fix` frequently to avoid large fix sessions
- Keep dependencies updated to avoid compatibility issues
- Use IDE integration for real-time feedback

## Getting Help

- Run `make help` for available commands
- Check the scripts in `scripts/` for detailed implementations
- Refer to tool-specific documentation:
  - [Black](https://black.readthedocs.io/)
  - [ESLint](https://eslint.org/)
  - [MyPy](https://mypy.readthedocs.io/)
  - [Prettier](https://prettier.io/)
  - [Pre-commit](https://pre-commit.com/)

This setup ensures that code quality issues are caught and fixed locally before they reach the CI pipeline or affect other developers.
