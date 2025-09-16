#!/bin/bash

# SprintSense Automation Status Check
# Shows the current status of all automated quality assurance tools

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_separator() {
    echo -e "${BLUE}================================================${NC}"
}

print_separator
print_status "🔍 SprintSense Automation Status"
print_separator

# Check pre-commit installation
print_status "Checking pre-commit framework..."
if command -v pre-commit &> /dev/null; then
    print_success "Pre-commit framework installed ($(pre-commit --version))"
else
    print_error "Pre-commit framework not installed"
fi

# Check Git hooks
print_status "Checking Git hooks..."
if [[ -f .git/hooks/pre-commit ]]; then
    print_success "Pre-commit hook installed"
else
    print_error "Pre-commit hook not installed"
fi

if [[ -f .git/hooks/pre-push ]]; then
    print_success "Pre-push hook installed"
else
    print_error "Pre-push hook not installed"
fi

if [[ -f .git/hooks/custom/enhanced-pre-commit ]]; then
    print_success "Enhanced pre-commit hook installed"
else
    print_warning "Enhanced pre-commit hook not installed"
fi

if [[ -f .git/hooks/custom/enhanced-pre-push ]]; then
    print_success "Enhanced pre-push hook installed"
else
    print_warning "Enhanced pre-push hook not installed"
fi

# Check quality tools
print_status "Checking quality tools..."

# Backend tools
if [[ -d "backend" ]]; then
    cd backend
    if command -v poetry &> /dev/null; then
        print_success "Poetry available for backend"

        # Check if tools are available in poetry env
        if poetry run black --version &> /dev/null; then
            print_success "Black formatter available"
        else
            print_error "Black formatter not available in poetry env"
        fi

        if poetry run isort --version &> /dev/null; then
            print_success "isort import sorter available"
        else
            print_error "isort not available in poetry env"
        fi

        if poetry run mypy --version &> /dev/null; then
            print_success "MyPy type checker available"
        else
            print_error "MyPy not available in poetry env"
        fi

        if poetry run pytest --version &> /dev/null; then
            print_success "Pytest testing framework available"
        else
            print_error "Pytest not available in poetry env"
        fi
    else
        print_error "Poetry not available for backend"
    fi
    cd ..
fi

# Frontend tools
if [[ -d "frontend" ]]; then
    cd frontend
    if command -v npm &> /dev/null; then
        print_success "npm available for frontend"

        # Check if tools are available
        if npm list eslint &> /dev/null; then
            print_success "ESLint linter available"
        else
            print_error "ESLint not installed in frontend"
        fi

        if npm list prettier &> /dev/null; then
            print_success "Prettier formatter available"
        else
            print_error "Prettier not installed in frontend"
        fi

        if npm list typescript &> /dev/null; then
            print_success "TypeScript compiler available"
        else
            print_error "TypeScript not installed in frontend"
        fi

        if npm list vitest &> /dev/null; then
            print_success "Vitest testing framework available"
        else
            print_error "Vitest not installed in frontend"
        fi
    else
        print_error "npm not available for frontend"
    fi
    cd ..
fi

# Check additional automation tools
print_status "Checking additional automation..."

if command -v fswatch &> /dev/null; then
    print_success "fswatch file watcher available"
else
    print_warning "fswatch not installed (needed for real-time file watching)"
    echo "           Install with: brew install fswatch"
fi

if command -v make &> /dev/null; then
    print_success "Make build system available"
else
    print_error "Make not available"
fi

# Check configuration files
print_status "Checking configuration files..."

if [[ -f .pre-commit-config.yaml ]]; then
    print_success "Pre-commit configuration found"
else
    print_error "Pre-commit configuration missing"
fi

if [[ -f Makefile ]]; then
    print_success "Makefile found"
else
    print_error "Makefile missing"
fi

if [[ -f .vscode/settings.json ]]; then
    print_success "VS Code workspace settings found"
else
    print_warning "VS Code workspace settings not configured"
fi

if [[ -f .vscode/tasks.json ]]; then
    print_success "VS Code tasks configured"
else
    print_warning "VS Code tasks not configured"
fi

if [[ -f .vscode/extensions.json ]]; then
    print_success "VS Code extensions recommended"
else
    print_warning "VS Code extension recommendations not configured"
fi

print_separator
print_status "📊 Automation Summary"
print_separator

echo -e "${GREEN}Available Commands:${NC}"
echo "  make help           # Show all make commands"
echo "  make install-hooks  # Install all Git hooks"
echo "  make fix            # Auto-fix quality issues"
echo "  make check          # Run quality checks"
echo "  make pre-commit     # Fix + check workflow"
echo "  ./scripts/watch-quality.sh  # Real-time file watching"

echo -e "${GREEN}VS Code Integration:${NC}"
echo "  Cmd+Shift+P → 'Tasks: Run Task' → Select quality task"
echo "  Automatic formatting on save (if extensions installed)"
echo "  Real-time error highlighting and type checking"

echo -e "${GREEN}Git Integration:${NC}"
echo "  Hooks run automatically on commit and push"
echo "  Pre-commit hooks format code and run checks"
echo "  Pre-push hooks run comprehensive tests"

if [[ -f .git/hooks/pre-commit && -f .pre-commit-config.yaml ]]; then
    print_success "Automation is fully configured and ready!"
else
    print_warning "Run 'make install-hooks' to complete automation setup"
fi

print_separator
