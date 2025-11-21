"""Unit tests for transaction service edge cases."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.bot.models.transaction import Transaction
from src.bot.services.transaction_service import TransactionService
from src.bot.utils.errors import ValidationError


class TestTransactionServiceEdgeCases:
    """Test transaction service edge cases."""

    @pytest.fixture
    def mock_session(self):
        """Create mock database session."""
        return AsyncMock()

    @pytest.fixture
    def transaction_service(self, mock_session):
        """Create transaction service instance."""
        return TransactionService(mock_session)

    @pytest.mark.asyncio
    async def test_create_transaction_zero_amount(self, transaction_service):
        """Test create_transaction with zero amount."""
        with pytest.raises(ValidationError, match="positive"):
            await transaction_service.create_transaction(
                user_id=123,
                transaction_data={
                    "amount": Decimal("0"),
                    "type": "expense",
                    "category": "Food",
                },
            )

    @pytest.mark.asyncio
    async def test_get_transactions_empty_result(self, transaction_service, mock_session):
        """Test get_transactions with empty result."""
        # Mock execute to return empty result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        transactions = await transaction_service.get_transactions(123)

        assert transactions == []

    @pytest.mark.asyncio
    async def test_get_transactions_with_filters(self, transaction_service, mock_session):
        """Test get_transactions with filters."""
        from datetime import datetime, timedelta

        # Create mock transaction
        mock_transaction = Transaction(
            id=1,
            user_id=123,
            amount=Decimal("50000"),
            type="expense",
            category="Food",
            timestamp=datetime.now(),
        )

        # Mock execute to return transaction
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_transaction]
        mock_session.execute = AsyncMock(return_value=mock_result)

        transactions = await transaction_service.get_transactions(
            123,
            filters={
                "type": "expense",
                "category": "Food",
                "start_date": datetime.now() - timedelta(days=7),
                "end_date": datetime.now(),
            },
        )

        assert len(transactions) == 1

    @pytest.mark.asyncio
    async def test_get_transactions_pagination(self, transaction_service, mock_session):
        """Test get_transactions with pagination."""
        # Create mock transactions
        mock_transactions = [
            Transaction(
                id=i,
                user_id=123,
                amount=Decimal("10000"),
                type="expense",
                category="Food",
                timestamp=datetime.now(),
            )
            for i in range(5)
        ]

        # Mock execute
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_transactions
        mock_session.execute = AsyncMock(return_value=mock_result)

        transactions = await transaction_service.get_transactions(123, page=2, per_page=5)

        assert len(transactions) == 5
