#!/bin/bash

# SprintSense File Watcher for Real-time Quality Checks
# Watches file changes and runs appropriate quality checks automatically

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] ✅ $1${NC}"
}

print_error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] ❌ $1${NC}"
}

print_separator() {
    echo -e "${BLUE}================================================${NC}"
}

# Check if fswatch is installed
if ! command -v fswatch &> /dev/null; then
    print_error "fswatch is not installed."
    echo "Install it with: brew install fswatch"
    exit 1
fi

print_separator
print_status "🔍 SprintSense File Watcher Started"
print_status "Watching for changes in backend/ and frontend/ directories..."
print_separator

# Function to run backend quality checks
run_backend_checks() {
    local file="$1"
    print_status "Backend file changed: $file"

    if [[ -d "backend" ]]; then
        cd backend

        # Run formatting only on the changed file if it's Python
        if [[ "$file" == *.py ]]; then
            print_status "Running Black formatting on $file..."
            poetry run black "$file" 2>/dev/null && print_success "Formatting applied" || print_error "Formatting failed"

            print_status "Running isort on $file..."
            poetry run isort "$file" --profile black 2>/dev/null && print_success "Import sorting applied" || print_error "Import sorting failed"

            # Type checking for the specific file
            print_status "Running MyPy type check on $file..."
            poetry run mypy "$file" --ignore-missing-imports 2>/dev/null && print_success "Type check passed" || print_error "Type check failed"
        fi

        cd ..
    fi
}

# Function to run frontend quality checks
run_frontend_checks() {
    local file="$1"
    print_status "Frontend file changed: $file"

    if [[ -d "frontend" ]]; then
        cd frontend

        # Run formatting only on the changed file if it's TS/TSX
        if [[ "$file" == *.ts || "$file" == *.tsx ]]; then
            print_status "Running Prettier formatting on $file..."
            npx prettier --write "$file" 2>/dev/null && print_success "Formatting applied" || print_error "Formatting failed"

            print_status "Running ESLint on $file..."
            npx eslint --fix "$file" 2>/dev/null && print_success "Linting passed" || print_error "Linting failed"
        fi

        cd ..
    fi
}

# Function to handle file changes
handle_file_change() {
    local file="$1"

    # Skip hidden files, node_modules, .git, etc.
    if [[ "$file" == *"/.git/"* || "$file" == *"/node_modules/"* || "$file" == *"/.venv/"* || "$file" == *"/__pycache__/"* ]]; then
        return
    fi

    # Skip temporary files
    if [[ "$file" == *"~" || "$file" == *".tmp" || "$file" == *".swp" ]]; then
        return
    fi

    # Determine which checks to run based on file path
    if [[ "$file" == */backend/* ]]; then
        run_backend_checks "$file"
    elif [[ "$file" == */frontend/* ]]; then
        run_frontend_checks "$file"
    fi
}

# Cleanup function
cleanup() {
    print_status "Stopping file watcher..."
    kill $(jobs -p) 2>/dev/null || true
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Watch for file changes
print_status "Press Ctrl+C to stop watching..."

fswatch -0 -r -l 1 backend/ frontend/ | while IFS= read -r -d '' file; do
    handle_file_change "$file"
done &

# Keep the script running
while true; do
    sleep 1
done
