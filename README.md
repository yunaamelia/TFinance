# FinancialAssist - Telegram AI Financial Assistant Bot

A Telegram bot integrated with AI that serves as a personal financial assistant, featuring interactive inline keyboards, JARVIS persona (Tony Stark's AI assistant), and comprehensive transaction management.

## Features

- 💰 **Transaction Recording**: Record income and expense transactions through conversational interface
- 🤖 **AI-Powered Insights**: JARVIS persona provides financial insights and personalized recommendations
- 📊 **Financial Summary**: View financial summaries, transaction history, and categorized reports
- 🧭 **Smart Navigation**: Consistent navigation controls (Home, Back, Help) across all screens

## Tech Stack

- **Language**: Python 3.11+
- **Framework**: python-telegram-bot v20+
- **AI**: OpenAI GPT-4 with JARVIS persona
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Caching**: Redis
- **Testing**: pytest with 70/25/5 testing pyramid

## Setup

### Prerequisites

- Python 3.11 or higher
- PostgreSQL (for production) or SQLite (for development)
- Redis (optional, for session caching)
- Telegram Bot Token from [@BotFather](https://t.me/botfather)
- OpenAI API Key

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd financialassist
```

1. Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

1. Install dependencies:

```bash
pip install -r requirements.txt
```

1. Configure environment:

```bash
cp .env.example .env
# Edit .env with your credentials
```

1. Run database migrations:

```bash
alembic upgrade head
```

1. Seed default categories:

```bash
python scripts/seed_categories.py
```

1. Start the bot:

```bash
python -m src.bot.main
```

## Docker Deployment

```bash
docker-compose up -d
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test type
pytest tests/unit/        # Unit tests
pytest tests/integration/ # Integration tests
pytest tests/e2e/        # E2E tests
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking (if using mypy)
mypy src/
```

### Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com) to ensure code quality before commits. The hooks automatically:

- ✅ Run full test suite (on pre-push)
- ✅ Check code quality with Ruff
- ✅ Format code with Ruff/Black
- ✅ Validate YAML, JSON, TOML files
- ✅ Detect security issues (secrets, private keys)
- ✅ Check for trailing whitespace and file formatting
- ✅ Run security linter (Bandit)

#### Setup Pre-commit

```bash
# Install pre-commit hooks
./scripts/setup-pre-commit.sh

# Or manually:
pip install pre-commit
pre-commit install --install-hooks
pre-commit install --hook-type pre-push
```

#### Usage

Pre-commit hooks run automatically on `git commit` and `git push`. To run manually:

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run

# Run specific hook
pre-commit run ruff-check --all-files
pre-commit run pytest --all-files
```

#### Skip Hooks (Not Recommended)

```bash
# Skip pre-commit hooks (use with caution!)
git commit --no-verify
```

**Note**: Full test suite runs on `pre-push` stage to avoid slowing down commits. Code quality checks run on `pre-commit` stage.

## Project Structure

```
src/bot/
├── handlers/      # Telegram bot handlers
├── keyboards/     # Inline keyboard builders
├── services/      # Business logic services
├── models/        # Database models
├── utils/         # Utility functions
└── config/        # Configuration management

tests/
├── unit/          # Unit tests (70%)
├── integration/   # Integration tests (25%)
└── e2e/           # E2E tests (5%)
```

## Constitution Compliance

This project adheres to the FinancialAssist Constitution:

- **Code Quality**: SOLID principles, complexity < 10, functions < 50 lines
- **Testing**: 70/25/5 pyramid, 80% coverage, TDD approach
- **UX**: WCAG 2.2 Level AA, consistent navigation, design tokens
- **Performance**: < 2s response time, Core Web Vitals compliance

## License

[Your License Here]

## Contributing

[Contributing Guidelines]
