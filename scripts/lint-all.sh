#!/bin/bash

# SprintSense - Comprehensive Linting and Quality Checks
# This script runs all the same checks that run in CI/CD

set -e  # Exit on any error

echo "🚀 Running SprintSense Quality Checks..."
echo "======================================"

# Check if we're in the project root
if [ ! -f ".pre-commit-config.yaml" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "📋 1/5 Running pre-commit hooks..."
if pre-commit run --all-files; then
    echo "✅ Pre-commit hooks passed"
else
    echo "❌ Pre-commit hooks failed"
    exit 1
fi

echo ""
echo "🔍 2/5 Running frontend linting..."
cd frontend
if npm run lint; then
    echo "✅ Frontend linting passed"
else
    echo "❌ Frontend linting failed"
    exit 1
fi

echo ""
echo "🎨 3/5 Checking frontend formatting..."
if npm run format:check; then
    echo "✅ Frontend formatting is correct"
else
    echo "❌ Frontend formatting check failed"
    echo "💡 Run 'npm run format' to fix formatting issues"
    exit 1
fi

echo ""
echo "🧪 4/5 Running frontend tests..."
if npm run test:run; then
    echo "✅ Frontend tests passed"
else
    echo "❌ Frontend tests failed"
    exit 1
fi

echo ""
echo "🔧 5/5 Running backend checks..."
cd ../backend
if poetry run pytest tests/ -q; then
    echo "✅ Backend tests passed"
else
    echo "❌ Backend tests failed"
    exit 1
fi

echo ""
echo "🎉 All quality checks passed!"
echo "Your code is ready for commit and push."
