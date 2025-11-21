"""Unit tests for AI service final coverage."""

from unittest.mock import MagicMock

import pytest

from src.bot.services.ai_service import OpenAIService


class TestAIServiceFinal:
    """Test AI service for final coverage."""

    @pytest.fixture
    def ai_service(self):
        """Create AI service instance."""
        return OpenAIService()

    @pytest.mark.asyncio
    async def test_generate_response_empty_content(self, ai_service, mocker):
        """Test generate_response when response has empty content."""
        from openai import AsyncOpenAI

        # Mock OpenAI client
        mock_client = mocker.MagicMock(spec=AsyncOpenAI)
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = None  # Empty content
        mock_client.chat.completions.create = mocker.AsyncMock(return_value=mock_response)
        ai_service.client = mock_client

        user_context = {
            "user_id": 123,
            "recent_transactions": [],
            "financial_summary": {},
        }

        result = await ai_service.generate_response("Hello", user_context, stream=False)

        # Should return empty string
        assert result == ""
