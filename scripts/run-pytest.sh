#!/bin/bash
# Script to run pytest with coverage, gracefully handling missing pytest

if python -m pytest --version > /dev/null 2>&1; then
    # Run tests with coverage
    # Exit code is propagated to pre-push hook to block push on test failures
    python -m pytest --cov=src --cov-report=term-missing --tb=short --maxfail=5
    exit_code=$?

    if [ $exit_code -ne 0 ]; then
        echo "❌ Tests failed. Please fix failing tests before pushing."
        echo "   Exit code: $exit_code"
    fi

    # Propagate pytest exit code to pre-push hook
    exit $exit_code
else
    echo "Note: pytest not installed. Install with: pip install -r requirements.txt"
    exit 0
fi
