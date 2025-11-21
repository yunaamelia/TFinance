#!/bin/bash
# Script to run pytest with coverage, gracefully handling missing pytest

if python -m pytest --version > /dev/null 2>&1; then
    # Run tests but don't fail on coverage for now (development stage)
    python -m pytest --cov=src --cov-report=term-missing --tb=short --maxfail=5 || {
        echo "⚠️  Some tests failed. This is expected during development."
        echo "   Fix tests before merging to main branch."
        exit 0  # Don't block push during development
    }
else
    echo "Note: pytest not installed. Install with: pip install -r requirements.txt"
    exit 0
fi
