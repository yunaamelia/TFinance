"""Unit tests for transaction service to increase coverage."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.bot.models.transaction import Transaction
from src.bot.services.transaction_service import TransactionService
from src.bot.utils.errors import DatabaseError, ValidationError


class TestTransactionServiceCoverage:
    """Test transaction service to increase coverage."""

    @pytest.fixture
    def mock_session(self):
        """Create mock database session."""
        return AsyncMock()

    @pytest.fixture
    def transaction_service(self, mock_session):
        """Create transaction service instance."""
        return TransactionService(mock_session)

    @pytest.mark.asyncio
    async def test_create_transaction_with_string_amount(self, transaction_service):
        """Test create_transaction with string amount."""
        transaction_data = {
            "amount": "50000",
            "type": "expense",
            "category": "Food",
            "description": "Lunch",
        }

        # Mock session
        mock_transaction = Transaction(
            id=1,
            user_id=123,
            amount=Decimal("50000"),
            type="expense",
            category="Food",
            timestamp=datetime.now(),
        )
        transaction_service.session.add = MagicMock()
        transaction_service.session.commit = AsyncMock()
        transaction_service.session.refresh = AsyncMock()

        # Mock the transaction creation by patching Transaction constructor
        from unittest.mock import patch

        with patch(
            "src.bot.services.transaction_service.Transaction",
            return_value=mock_transaction,
        ):
            result = await transaction_service.create_transaction(123, transaction_data)

        assert result.amount == Decimal("50000")

    @pytest.mark.asyncio
    async def test_create_transaction_invalid_amount_type(self, transaction_service):
        """Test create_transaction with invalid amount type."""
        transaction_data = {
            "amount": 50000,  # int instead of Decimal or string
            "type": "expense",
            "category": "Food",
        }

        with pytest.raises(ValidationError, match="Decimal or string"):
            await transaction_service.create_transaction(123, transaction_data)

    @pytest.mark.asyncio
    async def test_create_transaction_database_error(self, transaction_service, mock_session):
        """Test create_transaction when database error occurs."""
        from src.bot.utils.errors import DatabaseError

        transaction_data = {
            "amount": Decimal("50000"),
            "type": "expense",
            "category": "Food",
        }

        # Mock session.commit to raise error
        mock_session.commit = AsyncMock(side_effect=Exception("Database error"))
        mock_session.rollback = AsyncMock()

        with pytest.raises(DatabaseError):
            await transaction_service.create_transaction(123, transaction_data)

        # Should call rollback
        mock_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_transactions_database_error(self, transaction_service, mock_session):
        """Test get_transactions when database error occurs."""
        # Mock session.execute to raise error
        mock_session.execute = AsyncMock(side_effect=Exception("Database error"))

        with pytest.raises(DatabaseError):
            await transaction_service.get_transactions(123)
