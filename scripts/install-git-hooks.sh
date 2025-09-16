#!/bin/bash

# SprintSense Git Hooks Installation Script
# Automates the setup of all Git hooks for quality assurance

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
print_status "🔧 Installing SprintSense Git Hooks"
print_separator

# Check if we're in the correct directory
if [[ ! -d "backend" && ! -d "frontend" ]]; then
    print_error "Please run this script from the SprintSense root directory"
    exit 1
fi

# Install pre-commit
print_status "Installing pre-commit framework..."
if command -v pip &> /dev/null; then
    pip install pre-commit || {
        print_error "Failed to install pre-commit"
        exit 1
    }
    print_success "Pre-commit framework installed"
else
    print_error "pip not found. Please install Python and pip first."
    exit 1
fi

# Install pre-commit hooks
print_status "Installing pre-commit hooks..."
pre-commit install || {
    print_error "Failed to install pre-commit hooks"
    exit 1
}
print_success "Pre-commit hooks installed"

# Install pre-push hooks
print_status "Installing pre-push hooks..."
pre-commit install --hook-type pre-push || {
    print_error "Failed to install pre-push hooks"
    exit 1
}
print_success "Pre-push hooks installed"

# Install commit-msg hooks (for future use)
print_status "Installing commit-msg hooks..."
pre-commit install --hook-type commit-msg || true
print_success "Commit-msg hooks installed"

# Create custom git hooks directory
print_status "Setting up custom Git hooks..."
mkdir -p .git/hooks/custom

# Create enhanced pre-commit hook
cat > .git/hooks/custom/enhanced-pre-commit << 'EOF'
#!/bin/bash
# Enhanced Pre-commit Hook for SprintSense

echo "🔍 Running SprintSense quality checks..."

# Run pre-commit hooks first
if ! pre-commit run --all-files; then
    echo "❌ Pre-commit hooks failed"
    exit 1
fi

# Additional custom checks can go here
echo "✅ All quality checks passed!"
EOF

chmod +x .git/hooks/custom/enhanced-pre-commit

# Create enhanced pre-push hook
cat > .git/hooks/custom/enhanced-pre-push << 'EOF'
#!/bin/bash
# Enhanced Pre-push Hook for SprintSense

echo "🚀 Running pre-push quality checks..."

# Run comprehensive tests
if [[ -d "backend" ]]; then
    echo "Running backend tests..."
    cd backend
    if ! poetry run pytest tests/ -q; then
        echo "❌ Backend tests failed"
        exit 1
    fi
    cd ..
fi

if [[ -d "frontend" ]]; then
    echo "Running frontend tests..."
    cd frontend
    if ! npm run test:run; then
        echo "❌ Frontend tests failed"
        exit 1
    fi
    cd ..
fi

echo "✅ All pre-push checks passed!"
EOF

chmod +x .git/hooks/custom/enhanced-pre-push

print_success "Custom Git hooks created"

# Update the main hooks to call our enhanced versions
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# SprintSense Pre-commit Hook

# Run pre-commit framework
pre-commit run --hook-stage pre-commit

# Run our enhanced checks
if [[ -f .git/hooks/custom/enhanced-pre-commit ]]; then
    .git/hooks/custom/enhanced-pre-commit
fi
EOF

chmod +x .git/hooks/pre-commit

cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
# SprintSense Pre-push Hook

# Run pre-commit framework for push stage
pre-commit run --hook-stage pre-push

# Run our enhanced pre-push checks
if [[ -f .git/hooks/custom/enhanced-pre-push ]]; then
    .git/hooks/custom/enhanced-pre-push
fi
EOF

chmod +x .git/hooks/pre-push

# Test the installation
print_status "Testing Git hooks installation..."
if pre-commit run --all-files --hook-stage manual; then
    print_success "Git hooks test passed"
else
    print_error "Git hooks test failed - please check configuration"
    exit 1
fi

print_separator
print_success "🎉 Git Hooks Installation Complete!"
print_separator

echo -e "${GREEN}Installed hooks:${NC}"
echo "  ✅ Pre-commit: Runs on every commit"
echo "  ✅ Pre-push: Runs before every push"
echo "  ✅ Custom enhancements: Additional quality checks"

echo -e "${GREEN}Next steps:${NC}"
echo "  1. Test with: git commit (will trigger automatically)"
echo "  2. Push code: git push (will run comprehensive tests)"
echo "  3. Use 'make pre-commit' for manual checking"

echo -e "${YELLOW}Note:${NC} Hooks will now run automatically on every commit and push!"
EOF
