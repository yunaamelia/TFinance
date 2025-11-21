"""Unit tests for transaction service final coverage."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.bot.models.transaction import Transaction
from src.bot.services.transaction_service import TransactionService
from src.bot.utils.errors import DatabaseError


class TestTransactionServiceFinal:
    """Test transaction service for final coverage."""

    @pytest.fixture
    def mock_session(self):
        """Create mock database session."""
        return AsyncMock()

    @pytest.fixture
    def transaction_service(self, mock_session):
        """Create transaction service instance."""
        return TransactionService(mock_session)

    @pytest.mark.asyncio
    async def test_get_transaction_by_id_success(self, transaction_service, mock_session):
        """Test get_transaction_by_id success."""
        mock_transaction = Transaction(
            id=1,
            user_id=123,
            amount=Decimal("50000"),
            type="expense",
            category="Food",
            timestamp=datetime.now(),
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_transaction
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await transaction_service.get_transaction_by_id(123, 1)

        assert result == mock_transaction
        assert result.id == 1

    @pytest.mark.asyncio
    async def test_get_transaction_by_id_not_found(self, transaction_service, mock_session):
        """Test get_transaction_by_id when transaction not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await transaction_service.get_transaction_by_id(123, 999)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_transaction_by_id_database_error(self, transaction_service, mock_session):
        """Test get_transaction_by_id when database error occurs."""
        mock_session.execute = AsyncMock(side_effect=Exception("Database error"))

        with pytest.raises(DatabaseError):
            await transaction_service.get_transaction_by_id(123, 1)
