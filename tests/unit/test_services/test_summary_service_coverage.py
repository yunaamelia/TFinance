"""Unit tests for summary service to increase coverage."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.bot.models.transaction import Transaction
from src.bot.services.summary_service import SummaryService


class TestSummaryServiceCoverage:
    """Test summary service to increase coverage."""

    @pytest.fixture
    def mock_session(self):
        """Create mock database session."""
        return AsyncMock()

    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client."""
        return AsyncMock()

    @pytest.fixture
    def summary_service(self, mock_session, mock_redis):
        """Create summary service instance."""
        return SummaryService(mock_session, mock_redis)

    @pytest.mark.asyncio
    async def test_get_period_dates_today(self, summary_service):
        """Test get_period_dates for today."""
        start, end = summary_service._get_period_dates("today")

        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert end >= start

    @pytest.mark.asyncio
    async def test_get_period_dates_week(self, summary_service):
        """Test get_period_dates for week."""
        start, end = summary_service._get_period_dates("week")

        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert (end - start).days <= 7

    @pytest.mark.asyncio
    async def test_get_period_dates_month(self, summary_service):
        """Test get_period_dates for month."""
        start, end = summary_service._get_period_dates("month")

        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert (end - start).days <= 31

    @pytest.mark.asyncio
    async def test_get_period_dates_default(self, summary_service):
        """Test get_period_dates with invalid period (defaults to month)."""
        start, end = summary_service._get_period_dates("invalid")

        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert (end - start).days <= 31

    @pytest.mark.asyncio
    async def test_get_financial_summary_with_cache(self, summary_service, mock_redis):
        """Test get_financial_summary with Redis cache."""
        import json

        # Mock Redis to return cached summary
        cached_summary = {
            "total_income": 100000.0,
            "total_expenses": 50000.0,
            "net_balance": 50000.0,
            "transaction_count": 5,
        }
        mock_redis.get = AsyncMock(return_value=json.dumps(cached_summary))

        result = await summary_service.get_financial_summary(123, "month")

        assert result["total_income"] == Decimal("100000")
        assert result["total_expenses"] == Decimal("50000")

    @pytest.mark.asyncio
    async def test_get_financial_summary_cache_miss(
        self, summary_service, mock_session, mock_redis
    ):
        """Test get_financial_summary when cache miss."""
        # Mock Redis to return None (cache miss)
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.set = AsyncMock()

        # Mock database query to return empty result
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await summary_service.get_financial_summary(123, "month")

        assert result["total_income"] == Decimal("0")
        assert result["total_expenses"] == Decimal("0")
        assert result["net_balance"] == Decimal("0")

    @pytest.mark.asyncio
    async def test_get_financial_summary_with_transactions(
        self, summary_service, mock_session, mock_redis
    ):
        """Test get_financial_summary with actual transactions."""
        # Mock Redis to return None (cache miss)
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.set = AsyncMock()

        # Create mock transactions
        mock_transactions = [
            Transaction(
                id=1,
                user_id=123,
                amount=Decimal("100000"),
                type="income",
                category="Salary",
                timestamp=datetime.now(),
            ),
            Transaction(
                id=2,
                user_id=123,
                amount=Decimal("50000"),
                type="expense",
                category="Food",
                timestamp=datetime.now(),
            ),
        ]

        # Mock database query
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_transactions
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await summary_service.get_financial_summary(123, "month")

        assert result["total_income"] == Decimal("100000")
        assert result["total_expenses"] == Decimal("50000")
        assert result["net_balance"] == Decimal("50000")

    @pytest.mark.asyncio
    async def test_get_category_breakdown_success(self, summary_service, mocker):
        """Test get_category_breakdown success."""
        # Mock get_financial_summary to return summary with category breakdown
        mocker.patch.object(
            summary_service,
            "get_financial_summary",
            new=AsyncMock(
                return_value={
                    "category_breakdown": {
                        "Food": Decimal("50000"),
                        "Transport": Decimal("30000"),
                    },
                },
            ),
        )

        result = await summary_service.get_category_breakdown(123, "month")

        assert "Food" in result
        assert result["Food"] == Decimal("50000")

    @pytest.mark.asyncio
    async def test_calculate_summary_income_only(self, summary_service):
        """Test calculate_summary with income only."""
        transactions = [
            Transaction(
                id=1,
                user_id=123,
                amount=Decimal("100000"),
                type="income",
                category="Salary",
                timestamp=datetime.now(),
            ),
        ]

        summary = summary_service._calculate_summary(123, transactions, "month")

        assert summary["total_income"] == Decimal("100000")
        assert summary["total_expenses"] == Decimal("0")
        assert summary["net_balance"] == Decimal("100000")

    @pytest.mark.asyncio
    async def test_calculate_summary_expenses_only(self, summary_service):
        """Test calculate_summary with expenses only."""
        transactions = [
            Transaction(
                id=1,
                user_id=123,
                amount=Decimal("50000"),
                type="expense",
                category="Food",
                timestamp=datetime.now(),
            ),
        ]

        summary = summary_service._calculate_summary(123, transactions, "month")

        assert summary["total_income"] == Decimal("0")
        assert summary["total_expenses"] == Decimal("50000")
        assert summary["net_balance"] == Decimal("-50000")

    @pytest.mark.asyncio
    async def test_get_category_breakdown_calculation(self, summary_service):
        """Test _get_category_breakdown calculation."""
        transactions = [
            Transaction(
                id=1,
                user_id=123,
                amount=Decimal("50000"),
                type="expense",
                category="Food",
                timestamp=datetime.now(),
            ),
            Transaction(
                id=2,
                user_id=123,
                amount=Decimal("30000"),
                type="expense",
                category="Transport",
                timestamp=datetime.now(),
            ),
            Transaction(
                id=3,
                user_id=123,
                amount=Decimal("20000"),
                type="expense",
                category="Food",
                timestamp=datetime.now(),
            ),
        ]

        breakdown = summary_service._get_category_breakdown(transactions)

        assert breakdown["Food"] == Decimal("70000")
        assert breakdown["Transport"] == Decimal("30000")
