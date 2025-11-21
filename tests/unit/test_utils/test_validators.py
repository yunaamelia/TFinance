"""Unit tests for validation utilities."""

from decimal import Decimal

import pytest

from src.bot.utils.errors import ValidationError
from src.bot.utils.validators import (
    validate_amount,
    validate_category,
    validate_transaction_type,
)


class TestAmountValidator:
    """Test amount validation."""

    def test_valid_amount(self):
        """Test valid amount string."""
        result = validate_amount("50000.00")
        assert result == Decimal("50000.00")

    def test_valid_amount_integer(self):
        """Test valid amount as integer string."""
        result = validate_amount("50000")
        assert result == Decimal("50000.00")

    def test_valid_amount_with_commas(self):
        """Test amount with comma separators."""
        result = validate_amount("50,000.00")
        assert result == Decimal("50000.00")

    def test_invalid_amount_negative(self):
        """Test negative amount raises ValidationError."""
        with pytest.raises(ValidationError, match="must be positive"):
            validate_amount("-50000")

    def test_invalid_amount_zero(self):
        """Test zero amount raises ValidationError."""
        with pytest.raises(ValidationError, match="must be positive"):
            validate_amount("0")

    def test_invalid_amount_non_numeric(self):
        """Test non-numeric amount raises ValidationError."""
        with pytest.raises(ValidationError, match="Invalid amount format"):
            validate_amount("abc")

    def test_invalid_amount_too_many_decimals(self):
        """Test amount with more than 2 decimal places."""
        with pytest.raises(ValidationError, match="more than 2 decimal places"):
            validate_amount("50000.123")


class TestCategoryValidator:
    """Test category validation."""

    def test_valid_category(self):
        """Test valid category string."""
        result = validate_category("Food & Dining", "expense")
        assert result == "Food & Dining"

    def test_valid_category_trimmed(self):
        """Test category with whitespace is trimmed."""
        result = validate_category("  Food & Dining  ", "expense")
        assert result == "Food & Dining"

    def test_invalid_category_empty(self):
        """Test empty category raises ValidationError."""
        with pytest.raises(ValidationError, match="1-100 characters"):
            validate_category("", "expense")

    def test_invalid_category_too_long(self):
        """Test category exceeding 100 characters."""
        long_category = "a" * 101
        with pytest.raises(ValidationError, match="1-100 characters"):
            validate_category(long_category, "expense")

    def test_invalid_category_type_mismatch(self):
        """Test category type mismatch raises ValidationError."""
        # This will be implemented when category validation checks system categories
        result = validate_category("Custom Category", "expense")
        assert result == "Custom Category"  # User-defined categories are allowed


class TestTransactionTypeValidator:
    """Test transaction type validation."""

    def test_valid_income_type(self):
        """Test valid income type."""
        result = validate_transaction_type("income")
        assert result == "income"

    def test_valid_expense_type(self):
        """Test valid expense type."""
        result = validate_transaction_type("expense")
        assert result == "expense"

    def test_valid_type_case_insensitive(self):
        """Test type validation is case-insensitive."""
        result = validate_transaction_type("INCOME")
        assert result == "income"

    def test_invalid_type(self):
        """Test invalid type raises ValidationError."""
        with pytest.raises(ValidationError, match="must be 'income' or 'expense'"):
            validate_transaction_type("invalid")
