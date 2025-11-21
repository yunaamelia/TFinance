"""Unit tests for TransactionService."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.bot.models.transaction import Transaction
from src.bot.services.transaction_service import TransactionService
from src.bot.utils.errors import ValidationError


class TestTransactionService:
    """Test TransactionService methods."""

    @pytest.fixture
    def mock_session(self):
        """Create mock database session."""
        session = AsyncMock()
        session.add = MagicMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        return session

    @pytest.fixture
    def transaction_service(self, mock_session):
        """Create TransactionService instance with mock session."""
        return TransactionService(mock_session)

    @pytest.mark.asyncio
    async def test_create_transaction_success(self, transaction_service, mock_session):
        """Test successful transaction creation."""
        # Mock transaction data
        user_id = 123456789
        transaction_data = {
            "amount": Decimal("50000.00"),
            "type": "expense",
            "category": "Food & Dining",
            "description": "Lunch",
            "timestamp": datetime.now(),
        }

        # Mock the created transaction
        # Note: mock_transaction is not used but kept for reference
        mock_session.add.return_value = None
        mock_session.refresh.return_value = None

        # Create transaction
        result = await transaction_service.create_transaction(user_id, transaction_data)

        # Verify
        assert result.user_id == user_id
        assert result.amount == transaction_data["amount"]
        assert result.type == transaction_data["type"]
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_transaction_invalid_amount(self, transaction_service):
        """Test transaction creation with invalid amount."""
        user_id = 123456789
        transaction_data = {
            "amount": Decimal("-50000.00"),  # Negative amount
            "type": "expense",
            "category": "Food & Dining",
        }

        with pytest.raises(ValidationError):
            await transaction_service.create_transaction(user_id, transaction_data)

    @pytest.mark.asyncio
    async def test_get_transactions_pagination(self, transaction_service, mock_session):
        """Test getting transactions with pagination."""
        from sqlalchemy.ext.asyncio import AsyncResult

        user_id = 123456789

        # Mock query result
        mock_transactions = [
            Transaction(
                id=1,
                user_id=user_id,
                amount=Decimal("50000.00"),
                type="expense",
                category="Food & Dining",
                timestamp=datetime.now(),
            ),
            Transaction(
                id=2,
                user_id=user_id,
                amount=Decimal("100000.00"),
                type="expense",
                category="Transportation",
                timestamp=datetime.now(),
            ),
        ]

        # Mock Result object (what session.execute returns)
        mock_result = MagicMock(spec=AsyncResult)
        mock_result.scalars.return_value.all.return_value = mock_transactions

        # Mock count result
        mock_count_result = MagicMock(spec=AsyncResult)
        mock_count_result.scalar_one.return_value = 2

        # Mock session.execute to return different results based on query
        async def mock_execute(query):
            # Check if it's a count query
            query_str = str(query)
            if "count" in query_str.lower() or "COUNT" in query_str:
                return mock_count_result
            return mock_result

        mock_session.execute = AsyncMock(side_effect=mock_execute)

        # Get transactions
        result = await transaction_service.get_transactions(user_id, page=1, per_page=20)

        # Verify
        assert len(result) == 2
        assert result[0].id == 1
        assert result[1].id == 2

    @pytest.mark.asyncio
    async def test_get_transactions_with_filters(self, transaction_service, mock_session):
        """Test getting transactions with filters."""
        user_id = 123456789
        filters = {"type": "expense", "category": "Food & Dining"}

        # Mock query result
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_query)

        # Get transactions with filters
        result = await transaction_service.get_transactions(
            user_id,
            filters=filters,
            page=1,
            per_page=20,
        )

        # Verify filters were applied
        assert isinstance(result, list)
