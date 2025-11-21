"""Unit tests for AIService."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.bot.config.persona import JARVIS_PERSONA_V1, build_jarvis_prompt
from src.bot.models.transaction import Transaction, TransactionType
from src.bot.services.ai_service import OpenAIService
from src.bot.utils.errors import AIServiceError


class TestJARVISPersonaPrompt:
    """Test JARVIS persona prompt generation."""

    def test_build_jarvis_prompt_basic(self):
        """Test basic prompt building."""
        prompt = build_jarvis_prompt()
        assert "JARVIS" in prompt
        assert "financial assistant" in prompt.lower()

    def test_build_jarvis_prompt_with_context(self):
        """Test prompt building with context."""
        prompt = build_jarvis_prompt(
            context_summary="User has 5 transactions",
            recent_transactions="Transaction 1, Transaction 2",
            financial_summary="Balance: 1000000",
        )
        assert "User has 5 transactions" in prompt
        assert "Transaction 1" in prompt
        assert "Balance: 1000000" in prompt


class TestOpenAIService:
    """Test OpenAIService implementation."""

    @pytest.fixture
    def ai_service(self):
        """Create OpenAIService instance."""
        with patch("src.bot.services.ai_service.AsyncOpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client
            service = OpenAIService(JARVIS_PERSONA_V1)
            service.client = mock_client
            return service

    def test_service_initialization(self, ai_service):
        """Test service initialization."""
        assert ai_service.persona_config == JARVIS_PERSONA_V1
        assert ai_service.model == "gpt-4o-mini"

    def test_build_context_summary(self, ai_service):
        """Test context summary building."""
        user_context = {
            "user_id": 123456789,
            "recent_transactions": [],
        }
        summary = ai_service._build_context_summary(user_context)
        assert "123456789" in summary

    def test_build_context_summary_with_transactions(self, ai_service):
        """Test context summary with transactions."""
        transactions = [
            Transaction(
                id=1,
                user_id=123456789,
                amount=Decimal("50000.00"),
                type=TransactionType.EXPENSE,
                category="Food",
                timestamp=datetime.now(),
            ),
        ]
        user_context = {
            "user_id": 123456789,
            "recent_transactions": transactions,
        }
        summary = ai_service._build_context_summary(user_context)
        assert "Recent transactions: 1" in summary

    def test_build_system_prompt(self, ai_service):
        """Test system prompt building."""
        user_context = {
            "user_id": 123456789,
            "recent_transactions": [],
            "financial_summary": {},
        }
        prompt = ai_service._build_system_prompt(user_context)
        assert "JARVIS" in prompt
        assert "123456789" in prompt

    @pytest.mark.asyncio
    async def test_generate_response_success(self, ai_service):
        """Test successful response generation."""
        # Mock OpenAI client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response from JARVIS"

        ai_service.client.chat.completions.create = AsyncMock(
            return_value=mock_response,
        )

        user_context = {
            "user_id": 123456789,
            "recent_transactions": [],
        }

        response = await ai_service.generate_response(
            "What did I spend most on?",
            user_context,
            stream=False,
        )

        assert "Test response from JARVIS" in response
        ai_service.client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_response_with_streaming(self, ai_service):
        """Test streaming response generation."""
        # Mock streaming response
        mock_chunk1 = MagicMock()
        mock_chunk1.choices = [MagicMock()]
        mock_chunk1.choices[0].delta.content = "Hello"

        mock_chunk2 = MagicMock()
        mock_chunk2.choices = [MagicMock()]
        mock_chunk2.choices[0].delta.content = " World"

        async def mock_stream():
            yield mock_chunk1
            yield mock_chunk2

        ai_service.client.chat.completions.create = AsyncMock(
            return_value=mock_stream(),
        )

        user_context = {
            "user_id": 123456789,
            "recent_transactions": [],
        }

        response_stream = await ai_service.generate_response(
            "Hello",
            user_context,
            stream=True,
        )

        # Collect streamed content
        content = ""
        async for chunk in response_stream:
            content += chunk

        assert "Hello" in content or "World" in content

    @pytest.mark.asyncio
    async def test_generate_response_error(self, ai_service):
        """Test error handling in response generation."""
        ai_service.client.chat.completions.create = AsyncMock(
            side_effect=Exception("API Error"),
        )

        user_context = {
            "user_id": 123456789,
            "recent_transactions": [],
        }

        with pytest.raises(AIServiceError):
            await ai_service.generate_response(
                "Test message",
                user_context,
                stream=False,
            )

    @pytest.mark.asyncio
    async def test_analyze_spending_pattern(self, ai_service):
        """Test spending pattern analysis."""
        result = await ai_service.analyze_spending_pattern(123456789, "month")

        assert isinstance(result, dict)
        assert "top_categories" in result
        assert "trends" in result
        assert "recommendations" in result
