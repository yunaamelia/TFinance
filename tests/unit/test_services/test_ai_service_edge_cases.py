"""Unit tests for AI service edge cases."""

from unittest.mock import MagicMock

import pytest
from openai import AsyncOpenAI

from src.bot.services.ai_service import OpenAIService
from src.bot.utils.errors import AIServiceError


class TestAIServiceEdgeCases:
    """Test AI service edge cases."""

    @pytest.fixture
    def ai_service(self):
        """Create AI service instance."""
        return OpenAIService()

    def test_build_context_summary_no_transactions(self, ai_service):
        """Test build_context_summary with no transactions."""
        user_context = {
            "user_id": 123,
            "recent_transactions": [],
            "financial_summary": {},
        }

        summary = ai_service._build_context_summary(user_context)

        assert "User ID: 123" in summary
        # When no transactions, it doesn't add "Recent transactions" line
        assert "User ID: 123" in summary

    def test_build_context_summary_with_transactions(self, ai_service):
        """Test build_context_summary with transactions."""
        from datetime import datetime
        from decimal import Decimal

        from src.bot.models.transaction import Transaction

        transactions = [
            Transaction(
                id=1,
                user_id=123,
                amount=Decimal("50000"),
                type="income",
                category="Salary",
                timestamp=datetime.now(),
            ),
            Transaction(
                id=2,
                user_id=123,
                amount=Decimal("25000"),
                type="expense",
                category="Food",
                timestamp=datetime.now(),
            ),
        ]

        user_context = {
            "user_id": 123,
            "recent_transactions": transactions,
            "financial_summary": {"net_balance": Decimal("25000")},
        }

        summary = ai_service._build_context_summary(user_context)

        assert "Recent income" in summary or "Recent expenses" in summary
        assert "Current balance" in summary

    def test_build_recent_transactions_summary_empty(self, ai_service):
        """Test build_recent_transactions_summary with empty list."""
        summary = ai_service._build_recent_transactions_summary([])

        assert summary == "No recent transactions."

    def test_build_recent_transactions_summary_with_transactions(self, ai_service):
        """Test build_recent_transactions_summary with transactions."""
        from datetime import datetime
        from decimal import Decimal

        from src.bot.models.transaction import Transaction

        transactions = [
            Transaction(
                id=1,
                user_id=123,
                amount=Decimal("50000"),
                type="income",
                category="Salary",
                timestamp=datetime.now(),
            ),
        ]

        summary = ai_service._build_recent_transactions_summary(transactions)

        assert "income" in summary.lower()
        assert "Salary" in summary

    def test_build_financial_summary_string_empty(self, ai_service):
        """Test build_financial_summary_string with empty dict."""
        summary = ai_service._build_financial_summary_string({})

        assert summary == "No financial summary available."

    def test_build_financial_summary_string_with_data(self, ai_service):
        """Test build_financial_summary_string with data."""
        from decimal import Decimal

        financial_summary = {
            "total_income": Decimal("100000"),
            "total_expenses": Decimal("50000"),
            "net_balance": Decimal("50000"),
        }

        summary = ai_service._build_financial_summary_string(financial_summary)

        assert "Total Income" in summary
        assert "Total Expenses" in summary
        assert "Net Balance" in summary

    def test_build_financial_summary_string_partial(self, ai_service):
        """Test build_financial_summary_string with partial data."""
        from decimal import Decimal

        financial_summary = {
            "total_income": Decimal("100000"),
        }

        summary = ai_service._build_financial_summary_string(financial_summary)

        assert "Total Income" in summary

    @pytest.mark.asyncio
    async def test_generate_response_streaming(self, ai_service, mocker):
        """Test generate_response with streaming enabled."""
        # Mock OpenAI client
        mock_client = mocker.MagicMock(spec=AsyncOpenAI)

        # Create async generator for streaming
        async def mock_stream():
            mock_chunk = MagicMock()
            mock_chunk.choices = [MagicMock()]
            mock_chunk.choices[0].delta = MagicMock()
            mock_chunk.choices[0].delta.content = "Hello"
            yield mock_chunk

        mock_client.chat.completions.create = mocker.AsyncMock(return_value=mock_stream())
        ai_service.client = mock_client

        user_context = {
            "user_id": 123,
            "recent_transactions": [],
            "financial_summary": {},
        }

        result = await ai_service.generate_response("Hello", user_context, stream=True)

        # Should return async iterator
        assert hasattr(result, "__aiter__")

        # Consume iterator
        chunks = []
        async for chunk in result:
            chunks.append(chunk)

        assert len(chunks) > 0

    @pytest.mark.asyncio
    async def test_generate_response_openai_error(self, ai_service, mocker):
        """Test generate_response when OpenAI API raises error."""
        # Mock OpenAI client to raise error
        mock_client = mocker.MagicMock(spec=AsyncOpenAI)
        mock_client.chat.completions.create = mocker.AsyncMock(side_effect=Exception("API error"))
        ai_service.client = mock_client

        user_context = {
            "user_id": 123,
            "recent_transactions": [],
            "financial_summary": {},
        }

        with pytest.raises(AIServiceError):
            await ai_service.generate_response("Hello", user_context, stream=False)

    @pytest.mark.asyncio
    async def test_analyze_spending_pattern(self, ai_service, mocker):
        """Test analyze_spending_pattern."""
        # analyze_spending_pattern returns a dict, not a string
        result = await ai_service.analyze_spending_pattern(123, period="month")

        assert isinstance(result, dict)
        assert "top_categories" in result
        assert "trends" in result
        assert "recommendations" in result
