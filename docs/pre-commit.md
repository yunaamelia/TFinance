# Pre-commit Hooks Setup

This document describes the pre-commit hooks configuration for the FinancialAssist project.

## Overview

Pre-commit hooks automatically run code quality checks, tests, and security scans before commits and pushes. This ensures code quality and prevents common issues from entering the repository.

## Features

### Pre-commit Stage (runs on `git commit`)

- ✅ **Code Formatting**: Ruff formatter and Black
- ✅ **Linting**: Ruff linter with auto-fix
- ✅ **File Validation**: YAML, JSON, TOML syntax checks
- ✅ **Code Quality**: Trailing whitespace, end-of-file fixes
- ✅ **Security**: Detect private keys, AWS credentials
- ✅ **Python Syntax**: AST validation
- ✅ **Markdown**: Linting and formatting

### Pre-push Stage (runs on `git push`)

- ✅ **Full Test Suite**: pytest with coverage (80% minimum)
- ✅ **Coverage Report**: Terminal and HTML reports

## Installation

### Quick Setup

```bash
./scripts/setup-pre-commit.sh
```

### Manual Setup

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install --install-hooks
pre-commit install --hook-type pre-push
```

## Usage

### Automatic Execution

Hooks run automatically on:
- `git commit` - Code quality checks
- `git push` - Full test suite

### Manual Execution

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run

# Run specific hook
pre-commit run ruff-check --all-files
pre-commit run pytest --all-files

# Run hooks for specific stage
pre-commit run --hook-stage pre-push
```

### Update Hooks

```bash
# Update hook versions
pre-commit autoupdate

# Reinstall hooks
pre-commit install --install-hooks
```

## Configuration

The configuration is in `.pre-commit-config.yaml`. Key sections:

### Hooks Included

1. **Meta Hooks**: Validate pre-commit config itself
2. **pre-commit-hooks**: General file checks and formatting
3. **Ruff**: Fast Python linter and formatter
4. **Black**: Code formatter (backup)
5. **Pytest**: Full test suite (pre-push only)
6. **detect-secrets**: Security scanning
7. **Bandit**: Python security linter
8. **markdownlint**: Markdown linting

### Excluded Files

The following are excluded from hooks:
- `migrations/` - Database migrations
- `venv/`, `.venv/` - Virtual environments
- `build/`, `dist/` - Build artifacts
- `__pycache__/` - Python cache
- `.pytest_cache/` - Test cache
- `.env*` - Environment files
- `.secrets.baseline` - Secrets baseline

## Troubleshooting

### Hooks Fail

If hooks fail:

1. **Review the error message** - Most hooks provide clear error messages
2. **Auto-fix issues** - Many hooks can auto-fix (Ruff, Black, etc.)
3. **Run manually** - `pre-commit run --all-files` to see all issues
4. **Skip if needed** - `git commit --no-verify` (not recommended)

### Tests Fail on Pre-push

If tests fail on pre-push:

1. **Run tests locally first**: `pytest --cov=src`
2. **Check coverage**: Ensure 80% coverage minimum
3. **Fix failing tests** before pushing

### Slow Pre-commit

If pre-commit is slow:

1. **Tests run on pre-push** - Not pre-commit (by design)
2. **Use `--hook-stage`** - Run specific stages only
3. **Skip hooks temporarily**: `git commit --no-verify` (use sparingly)

## Best Practices

1. **Don't skip hooks** - Fix issues instead of using `--no-verify`
2. **Run before commit** - Use `pre-commit run` to catch issues early
3. **Keep hooks updated** - Run `pre-commit autoupdate` regularly
4. **Review baseline** - Update `.secrets.baseline` when adding legitimate secrets

## References

- [Pre-commit Documentation](https://pre-commit.com)
- [Pre-commit Hooks](https://github.com/pre-commit/pre-commit-hooks)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Pytest Documentation](https://docs.pytest.org/)

