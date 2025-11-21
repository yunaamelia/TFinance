"""Unit tests for summary service edge cases."""

from unittest.mock import AsyncMock

import pytest

from src.bot.services.summary_service import SummaryService
from src.bot.utils.errors import DatabaseError


class TestSummaryServiceEdgeCases:
    """Test summary service edge cases."""

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
    async def test_get_category_breakdown_database_error(self, summary_service, mocker):
        """Test get_category_breakdown when database error occurs."""
        # Mock get_financial_summary to raise DatabaseError
        mocker.patch.object(
            summary_service,
            "get_financial_summary",
            new=AsyncMock(side_effect=DatabaseError("Database error", operation="query")),
        )

        with pytest.raises(DatabaseError):
            await summary_service.get_category_breakdown(123, "month")

    @pytest.mark.asyncio
    async def test_get_category_breakdown_generic_error(self, summary_service, mocker):
        """Test get_category_breakdown when generic error occurs."""
        # Mock get_financial_summary to raise generic exception
        mocker.patch.object(
            summary_service,
            "get_financial_summary",
            new=AsyncMock(side_effect=Exception("Unexpected error")),
        )

        with pytest.raises(DatabaseError):
            await summary_service.get_category_breakdown(123, "month")

    @pytest.mark.asyncio
    async def test_invalidate_cache(self, summary_service, mock_redis):
        """Test invalidate_cache."""
        await summary_service.invalidate_cache(123)

        # Should delete cache for all periods
        assert mock_redis.delete.call_count == 3  # today, week, month

    @pytest.mark.asyncio
    async def test_invalidate_cache_no_redis(self, summary_service):
        """Test invalidate_cache when Redis is None."""
        summary_service.redis = None

        # Should not raise exception
        await summary_service.invalidate_cache(123)
