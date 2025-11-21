"""Database models for FinancialAssist bot."""

from sqlalchemy.ext.declarative import declarative_base

# Create declarative base for all models
Base = declarative_base()

# Import all models to ensure they're registered with Base
# Import order matters for relationships
from src.bot.models.category import Category  # noqa: E402, F401
from src.bot.models.transaction import Transaction  # noqa: E402, F401
from src.bot.models.user import User  # noqa: E402, F401

__all__ = ["Base", "User", "Transaction", "Category"]
