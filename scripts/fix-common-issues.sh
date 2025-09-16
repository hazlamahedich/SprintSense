#!/bin/bash

# SprintSense Quick Fix Script
# Automatically fixes common formatting and linting issues

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

print_separator() {
    echo -e "${BLUE}================================================${NC}"
}

print_separator
print_status "🔧 SprintSense Quick Fix Script"
print_separator

# Backend fixes
if [[ -d "backend" ]]; then
    print_status "Fixing Backend Issues..."
    cd backend

    if command -v poetry &> /dev/null; then
        # Fix Python formatting
        print_status "Fixing Python code formatting (Black)..."
        poetry run black app tests migrations || true
        print_success "Black formatting applied"

        # Fix import sorting
        print_status "Fixing import sorting (isort)..."
        poetry run isort app tests migrations --profile black || true
        print_success "Import sorting applied"

        # Fix line length issues
        print_status "Fixing line length issues..."
        python3 ../scripts/fix-line-lengths.py app/**/*.py tests/**/*.py || true
        print_success "Line length fixes applied"

        # Auto-fix some flake8 issues (if autopep8 is available)
        if poetry run python -c "import autopep8" 2>/dev/null; then
            print_status "Auto-fixing Python code style issues..."
            find app tests -name "*.py" -exec poetry run autopep8 --in-place --aggressive --aggressive --max-line-length=88 {} \; || true
            print_success "Auto-fixes applied"
        fi
    else
        print_error "Poetry not found - skipping backend fixes"
    fi

    cd ..
fi

# Frontend fixes
if [[ -d "frontend" ]]; then
    print_status "Fixing Frontend Issues..."
    cd frontend

    if command -v npm &> /dev/null; then
        # Fix ESLint issues
        print_status "Fixing ESLint issues..."
        npm run lint:fix || true
        print_success "ESLint fixes applied"

        # Fix Prettier formatting
        print_status "Fixing code formatting (Prettier)..."
        npm run format || true
        print_success "Prettier formatting applied"
    else
        print_error "npm not found - skipping frontend fixes"
    fi

    cd ..
fi

# Git fixes
print_status "Applying Git fixes..."

# Remove trailing whitespace
print_status "Removing trailing whitespace..."
find . -type f \( -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) \
    -not -path "./.git/*" \
    -not -path "./node_modules/*" \
    -not -path "./.venv/*" \
    -not -path "./backend/.venv/*" \
    -exec sed -i '' 's/[[:space:]]*$//' {} \; 2>/dev/null || true
print_success "Trailing whitespace removed"

# Fix line endings (convert to LF)
print_status "Normalizing line endings..."
find . -type f \( -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) \
    -not -path "./.git/*" \
    -not -path "./node_modules/*" \
    -not -path "./.venv/*" \
    -not -path "./backend/.venv/*" \
    -exec dos2unix {} \; 2>/dev/null || true
print_success "Line endings normalized"

print_separator
print_success "🎉 Common issues fixed! Run pre-commit-checks.sh to verify."
print_separator

echo -e "${GREEN}Next steps:${NC}"
echo "  ./scripts/pre-commit-checks.sh    # Verify all fixes"
echo "  git add .                         # Stage the changes"
echo "  git commit -m 'fix: your message' # Commit the fixes"
