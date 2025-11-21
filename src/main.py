#!/usr/bin/env python3
"""Main entry point for FinancialAssist Telegram bot.

This is a wrapper that imports and runs the bot from src.bot.main
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.bot.main import main  # noqa: E402

if __name__ == "__main__":
    main()
