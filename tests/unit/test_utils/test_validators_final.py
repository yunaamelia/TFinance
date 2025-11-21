"""Unit tests for validators final coverage."""

from decimal import Decimal

import pytest

from src.bot.utils.errors import ValidationError
from src.bot.utils.validators import validate_amount, validate_category, validate_transaction_type


class TestValidatorsFinal:
    """Test validators for final coverage."""

    def test_validate_amount_with_comma(self):
        """Test validate_amount with comma separator."""
        result = validate_amount("50,000.50")

        assert result == Decimal("50000.50")

    def test_validate_amount_negative(self):
        """Test validate_amount with negative number."""
        with pytest.raises(ValidationError, match="positive"):
            validate_amount("-100")

    def test_validate_category_too_long(self):
        """Test validate_category with too long name."""
        long_category = "A" * 101
        with pytest.raises(ValidationError, match="1-100"):
            validate_category(long_category, "expense")

    def test_validate_transaction_type_invalid(self):
        """Test validate_transaction_type with invalid type."""
        with pytest.raises(ValidationError, match="'income' or 'expense'"):
            validate_transaction_type("invalid")
