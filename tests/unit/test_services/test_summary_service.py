"""Unit tests for SummaryService."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.bot.models.transaction import Transaction, TransactionType
from src.bot.services.summary_service import SummaryService


class TestSummaryService:
    """Test SummaryService methods."""

    @pytest.fixture
    def mock_session(self):
        """Create mock database session."""
        session = AsyncMock()
        return session

    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client."""
        redis_client = AsyncMock()
        return redis_client

    @pytest.fixture
    def summary_service(self, mock_session, mock_redis):
        """Create SummaryService instance."""
        return SummaryService(mock_session, mock_redis)

    @pytest.mark.asyncio
    async def test_get_period_dates_today(self, summary_service):
        """Test period date calculation for 'today'."""
        start, end = summary_service._get_period_dates("today")

        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert start.date() == datetime.now().date()
        assert end.date() == datetime.now().date()

    @pytest.mark.asyncio
    async def test_get_period_dates_week(self, summary_service):
        """Test period date calculation for 'week'."""
        start, end = summary_service._get_period_dates("week")

        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        # End should be today
        assert end.date() == datetime.now().date()
        # Start should be 7 days ago
        assert (end - start).days == 6  # Inclusive of today

    @pytest.mark.asyncio
    async def test_get_period_dates_month(self, summary_service):
        """Test period date calculation for 'month'."""
        start, end = summary_service._get_period_dates("month")

        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        # End should be today
        assert end.date() == datetime.now().date()
        # Start should be approximately 30 days ago
        assert (end - start).days >= 28
        assert (end - start).days <= 31

    @pytest.mark.asyncio
    async def test_calculate_summary_income_only(self, summary_service, mock_session):
        """Test summary calculation with income only."""
        # Mock transactions
        transactions = [
            Transaction(
                id=1,
                user_id=123456789,
                amount=Decimal("1000000.00"),
                type=TransactionType.INCOME,
                category="Salary",
                timestamp=datetime.now(),
            ),
            Transaction(
                id=2,
                user_id=123456789,
                amount=Decimal("500000.00"),
                type=TransactionType.INCOME,
                category="Freelance",
                timestamp=datetime.now(),
            ),
        ]

        summary = summary_service._calculate_summary(123456789, transactions, "month")

        assert summary["total_income"] == Decimal("1500000.00")
        assert summary["total_expenses"] == Decimal("0.00")
        assert summary["net_balance"] == Decimal("1500000.00")
        assert summary["transaction_count"] == 2

    @pytest.mark.asyncio
    async def test_calculate_summary_expenses_only(self, summary_service, mock_session):
        """Test summary calculation with expenses only."""
        transactions = [
            Transaction(
                id=1,
                user_id=123456789,
                amount=Decimal("50000.00"),
                type=TransactionType.EXPENSE,
                category="Food & Dining",
                timestamp=datetime.now(),
            ),
            Transaction(
                id=2,
                user_id=123456789,
                amount=Decimal("100000.00"),
                type=TransactionType.EXPENSE,
                category="Transportation",
                timestamp=datetime.now(),
            ),
        ]

        summary = summary_service._calculate_summary(123456789, transactions, "month")

        assert summary["total_income"] == Decimal("0.00")
        assert summary["total_expenses"] == Decimal("150000.00")
        assert summary["net_balance"] == Decimal("-150000.00")
        assert summary["transaction_count"] == 2

    @pytest.mark.asyncio
    async def test_calculate_summary_mixed(self, summary_service, mock_session):
        """Test summary calculation with income and expenses."""
        transactions = [
            Transaction(
                id=1,
                user_id=123456789,
                amount=Decimal("1000000.00"),
                type=TransactionType.INCOME,
                category="Salary",
                timestamp=datetime.now(),
            ),
            Transaction(
                id=2,
                user_id=123456789,
                amount=Decimal("50000.00"),
                type=TransactionType.EXPENSE,
                category="Food & Dining",
                timestamp=datetime.now(),
            ),
            Transaction(
                id=3,
                user_id=123456789,
                amount=Decimal("100000.00"),
                type=TransactionType.EXPENSE,
                category="Transportation",
                timestamp=datetime.now(),
            ),
        ]

        summary = summary_service._calculate_summary(123456789, transactions, "month")

        assert summary["total_income"] == Decimal("1000000.00")
        assert summary["total_expenses"] == Decimal("150000.00")
        assert summary["net_balance"] == Decimal("850000.00")
        assert summary["transaction_count"] == 3

    @pytest.mark.asyncio
    async def test_get_category_breakdown(self, summary_service, mock_session):
        """Test category breakdown calculation."""
        transactions = [
            Transaction(
                id=1,
                user_id=123456789,
                amount=Decimal("50000.00"),
                type=TransactionType.EXPENSE,
                category="Food & Dining",
                timestamp=datetime.now(),
            ),
            Transaction(
                id=2,
                user_id=123456789,
                amount=Decimal("30000.00"),
                type=TransactionType.EXPENSE,
                category="Food & Dining",
                timestamp=datetime.now(),
            ),
            Transaction(
                id=3,
                user_id=123456789,
                amount=Decimal("100000.00"),
                type=TransactionType.EXPENSE,
                category="Transportation",
                timestamp=datetime.now(),
            ),
        ]

        breakdown = summary_service._get_category_breakdown(transactions)

        assert breakdown["Food & Dining"] == Decimal("80000.00")
        assert breakdown["Transportation"] == Decimal("100000.00")

    @pytest.mark.asyncio
    async def test_get_financial_summary_with_cache(self, summary_service, mock_redis):
        """Test financial summary retrieval with Redis cache."""
        # Mock cached data
        cached_data = (
            '{"total_income": 1000000.00, "total_expenses": 500000.00, "net_balance": 500000.00}'
        )
        mock_redis.get = AsyncMock(return_value=cached_data)

        summary = await summary_service.get_financial_summary(123456789, "month")

        assert summary["total_income"] == Decimal("1000000.00")
        mock_redis.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_financial_summary_without_cache(
        self, summary_service, mock_session, mock_redis
    ):
        """Test financial summary calculation when cache miss."""
        # Mock cache miss
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.set = AsyncMock()

        # Mock database query
        mock_query = MagicMock()
        mock_query.where.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []

        mock_session.execute = AsyncMock(return_value=mock_query)

        summary = await summary_service.get_financial_summary(123456789, "month")

        assert summary is not None
        assert "total_income" in summary
        assert "total_expenses" in summary
        assert "net_balance" in summary

        # Verify cache was set
        mock_redis.set.assert_called_once()
