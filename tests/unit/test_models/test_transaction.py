"""Unit tests for Transaction model."""

from datetime import datetime
from decimal import Decimal

from src.bot.models.transaction import Transaction, TransactionType
from src.bot.models.user import User


class TestTransactionModel:
    """Test Transaction model validation and constraints."""

    def test_transaction_creation(self):
        """Test creating a valid transaction."""
        user = User(id=123456789, first_name="Test User")
        transaction = Transaction(
            user_id=user.id,
            amount=Decimal("50000.00"),
            type=TransactionType.EXPENSE,
            category="Food & Dining",
            description="Lunch",
            timestamp=datetime.now(),
        )

        assert transaction.user_id == user.id
        assert transaction.amount == Decimal("50000.00")
        assert transaction.type == TransactionType.EXPENSE
        assert transaction.category == "Food & Dining"
        assert transaction.description == "Lunch"
        assert transaction.deleted_at is None

    def test_transaction_income_type(self):
        """Test transaction with income type."""
        transaction = Transaction(
            user_id=123456789,
            amount=Decimal("1000000.00"),
            type=TransactionType.INCOME,
            category="Salary",
            timestamp=datetime.now(),
        )

        assert transaction.type == TransactionType.INCOME

    def test_transaction_expense_type(self):
        """Test transaction with expense type."""
        transaction = Transaction(
            user_id=123456789,
            amount=Decimal("50000.00"),
            type=TransactionType.EXPENSE,
            category="Food & Dining",
            timestamp=datetime.now(),
        )

        assert transaction.type == TransactionType.EXPENSE

    def test_transaction_with_tags(self):
        """Test transaction with optional tags."""
        transaction = Transaction(
            user_id=123456789,
            amount=Decimal("50000.00"),
            type=TransactionType.EXPENSE,
            category="Food & Dining",
            timestamp=datetime.now(),
            tags={"location": "Jakarta", "payment_method": "cash"},
        )

        assert transaction.tags == {"location": "Jakarta", "payment_method": "cash"}

    def test_transaction_soft_delete(self):
        """Test transaction soft delete functionality."""
        transaction = Transaction(
            user_id=123456789,
            amount=Decimal("50000.00"),
            type=TransactionType.EXPENSE,
            category="Food & Dining",
            timestamp=datetime.now(),
        )

        assert transaction.deleted_at is None
        transaction.deleted_at = datetime.now()
        assert transaction.deleted_at is not None
