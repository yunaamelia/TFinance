"""Seed default categories for the FinancialAssist bot."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select

from src.bot.config.settings import get_async_session_maker
from src.bot.models.category import Category, CategoryType

# Default categories
DEFAULT_CATEGORIES = [
    # Income categories
    {"name": "Salary", "type": CategoryType.INCOME, "icon": "💰", "is_system": True},
    {"name": "Freelance", "type": CategoryType.INCOME, "icon": "💼", "is_system": True},
    {"name": "Investment", "type": CategoryType.INCOME, "icon": "📈", "is_system": True},
    {"name": "Gift", "type": CategoryType.INCOME, "icon": "🎁", "is_system": True},
    {"name": "Other", "type": CategoryType.INCOME, "icon": "➕", "is_system": True},
    # Expense categories
    {"name": "Food & Dining", "type": CategoryType.EXPENSE, "icon": "🍔", "is_system": True},
    {"name": "Transportation", "type": CategoryType.EXPENSE, "icon": "🚗", "is_system": True},
    {"name": "Shopping", "type": CategoryType.EXPENSE, "icon": "🛒", "is_system": True},
    {"name": "Bills", "type": CategoryType.EXPENSE, "icon": "💳", "is_system": True},
    {"name": "Entertainment", "type": CategoryType.EXPENSE, "icon": "🎬", "is_system": True},
    {"name": "Health", "type": CategoryType.EXPENSE, "icon": "🏥", "is_system": True},
    {"name": "Education", "type": CategoryType.EXPENSE, "icon": "📚", "is_system": True},
    {"name": "Other", "type": CategoryType.EXPENSE, "icon": "➖", "is_system": True},
]


async def seed_categories():
    """Seed default categories into the database."""
    async_session_maker = get_async_session_maker()

    async with async_session_maker() as session:
        # Check if categories already exist
        result = await session.execute(select(Category).where(Category.is_system))
        existing_categories = result.scalars().all()

        if existing_categories:
            print(f"Found {len(existing_categories)} existing system categories. Skipping seed.")
            return

        # Create categories
        categories = []
        for cat_data in DEFAULT_CATEGORIES:
            category = Category(**cat_data)
            categories.append(category)
            session.add(category)

        await session.commit()
        print(f"Successfully seeded {len(categories)} default categories:")
        for cat in categories:
            print(f"  - {cat.icon} {cat.name} ({cat.type})")


if __name__ == "__main__":
    asyncio.run(seed_categories())
