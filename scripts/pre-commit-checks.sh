#!/bin/bash

# SprintSense Pre-Commit Quality Checks
# Run this script before committing to catch issues locally

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if we're in the correct directory
if [[ ! -d "backend" && ! -d "frontend" ]]; then
    print_error "Please run this script from the SprintSense root directory"
    exit 1
fi

print_separator
print_status "🚀 SprintSense Pre-Commit Quality Checks"
print_separator

# Backend Checks
if [[ -d "backend" ]]; then
    print_status "Running Backend Quality Checks..."
    cd backend

    # Check if poetry is available
    if ! command -v poetry &> /dev/null; then
        print_error "Poetry is not installed. Please install poetry first."
        exit 1
    fi

    # Install dependencies if needed
    print_status "Ensuring backend dependencies are installed..."
    poetry install || {
        print_error "Failed to install backend dependencies"
        exit 1
    }

    # 1. Black formatting check
    print_status "Checking Python code formatting (Black)..."
    if poetry run black --check app tests migrations; then
        print_success "Black formatting check passed"
    else
        print_error "Black formatting issues found. Run: cd backend && poetry run black app tests migrations"
        exit 1
    fi

    # 2. Import sorting check
    print_status "Checking import sorting (isort)..."
    if poetry run isort --check-only app tests migrations --profile black; then
        print_success "Import sorting check passed"
    else
        print_error "Import sorting issues found. Run: cd backend && poetry run isort app tests migrations --profile black"
        exit 1
    fi

    # 3. Flake8 linting
    print_status "Running Python linting (Flake8)..."
    if poetry run flake8 app tests --max-line-length=88 --extend-ignore=E203,W503,E501; then
        print_success "Flake8 linting passed"
    else
        print_error "Flake8 linting issues found"
        exit 1
    fi

    # 4. MyPy type checking
    print_status "Running type checking (MyPy)..."
    if poetry run mypy app --ignore-missing-imports; then
        print_success "MyPy type checking passed"
    else
        print_error "MyPy type checking issues found"
        exit 1
    fi

    # 5. Security check
    print_status "Running security check (Bandit)..."
    if poetry run bandit -r app -f json > /dev/null 2>&1; then
        print_success "Security check passed"
    else
        print_warning "Security check found potential issues (check manually if needed)"
    fi

    # 6. Backend tests
    print_status "Running backend tests..."
    if poetry run pytest tests/ -q; then
        print_success "All backend tests passed"
    else
        print_error "Backend tests failed"
        exit 1
    fi

    cd ..
fi

# Frontend Checks
if [[ -d "frontend" ]]; then
    print_status "Running Frontend Quality Checks..."
    cd frontend

    # Check if npm is available
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install Node.js and npm first."
        exit 1
    fi

    # Install dependencies if needed
    print_status "Ensuring frontend dependencies are installed..."
    npm ci || {
        print_error "Failed to install frontend dependencies"
        exit 1
    }

    # 1. TypeScript type checking
    print_status "Running TypeScript type checking..."
    if npm run type-check; then
        print_success "TypeScript type checking passed"
    else
        print_error "TypeScript type checking failed"
        exit 1
    fi

    # 2. ESLint checking
    print_status "Running ESLint checking..."
    if npm run lint; then
        print_success "ESLint checking passed"
    else
        print_error "ESLint issues found. Run: cd frontend && npm run lint:fix"
        exit 1
    fi

    # 3. Prettier formatting check
    print_status "Checking code formatting (Prettier)..."
    if npm run format:check; then
        print_success "Prettier formatting check passed"
    else
        print_error "Prettier formatting issues found. Run: cd frontend && npm run format"
        exit 1
    fi

    # 4. Frontend tests
    print_status "Running frontend tests..."
    if npm run test:run; then
        print_success "All frontend tests passed"
    else
        print_error "Frontend tests failed"
        exit 1
    fi

    cd ..
fi

# Git checks
print_status "Running Git checks..."

# Check for merge conflicts
if git diff --check HEAD~1; then
    print_success "No merge conflict markers found"
else
    print_error "Merge conflict markers found in files"
    exit 1
fi

# Check for large files
large_files=$(find . -type f -size +1M -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./.venv/*" -not -path "./backend/.venv/*" 2>/dev/null || true)
if [[ -n "$large_files" ]]; then
    print_warning "Large files detected:"
    echo "$large_files"
    print_warning "Consider using Git LFS for large files"
fi

# Documentation checks
if command -v markdownlint &> /dev/null; then
    print_status "Running Markdown linting..."
    if markdownlint . --ignore node_modules --ignore .git; then
        print_success "Markdown linting passed"
    else
        print_warning "Markdown linting issues found (non-critical)"
    fi
fi

print_separator
print_success "🎉 All quality checks passed! Ready to commit."
print_separator

echo -e "${GREEN}Next steps:${NC}"
echo "  git add ."
echo "  git commit -m 'your commit message'"
echo "  git push origin main"
