#!/bin/bash
# Setup script for pre-commit hooks
# This script installs and configures pre-commit hooks for the project

set -e

echo "🔧 Setting up pre-commit hooks..."

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    echo "❌ pre-commit is not installed. Installing..."
    pip install pre-commit
else
    echo "✅ pre-commit is already installed"
fi

# Install pre-commit hooks
echo "📦 Installing pre-commit hooks..."
pre-commit install --install-hooks

# Install hooks for pre-push stage
echo "📦 Installing pre-push hooks..."
pre-commit install --hook-type pre-push

# Run pre-commit on all files to test
echo "🧪 Testing pre-commit hooks on all files..."
pre-commit run --all-files || {
    echo "⚠️  Some hooks failed. Please fix the issues and try again."
    exit 1
}

echo "✅ Pre-commit hooks setup complete!"
echo ""
echo "To manually run hooks:"
echo "  pre-commit run --all-files"
echo ""
echo "To skip hooks (not recommended):"
echo "  git commit --no-verify"
