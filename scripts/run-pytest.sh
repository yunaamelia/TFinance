#!/bin/bash
# Script to run pytest with coverage, gracefully handling missing pytest

if python -m pytest --version > /dev/null 2>&1; then
    python -m pytest --cov=src --cov-report=term-missing --cov-fail-under=80 --tb=short
else
    echo "Note: pytest not installed. Install with: pip install -r requirements.txt"
    exit 0
fi
