"""Integration tests for AI API integration."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.bot.services.ai_service import OpenAIService
from src.bot.config.persona import JARVIS_PERSONA_V1


class TestAIServiceIntegration:
    """Integration tests for AI service with mocked API."""

    @pytest.mark.asyncio
    async def test_ai_service_with_mocked_openai(self):
        """Test AI service with mocked OpenAI API."""
        with patch("src.bot.services.ai_service.AsyncOpenAI") as mock_openai_class:
            # Setup mock client
            mock_client = AsyncMock()
            mock_openai_class.return_value = mock_client

            # Setup mock response
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = (
                "Good day, Sir. Based on your recent transactions, "
                "I've noticed you've spent 50,000 on Food & Dining this month."
            )

            mock_client.chat.completions.create = AsyncMock(
                return_value=mock_response,
            )

            # Create service and test
            service = OpenAIService(JARVIS_PERSONA_V1)
            user_context = {
                "user_id": 123456789,
                "recent_transactions": [],
                "financial_summary": {},
            }

            response = await service.generate_response(
                "What did I spend most on this month?",
                user_context,
                stream=False,
            )

            # Verify response
            assert response is not None
            assert len(response) > 0

            # Verify API was called
            mock_client.chat.completions.create.assert_called_once()
            call_args = mock_client.chat.completions.create.call_args
            assert call_args.kwargs["model"] == "gpt-4o-mini"
            assert len(call_args.kwargs["messages"]) > 0

    @pytest.mark.asyncio
    async def test_ai_service_streaming_integration(self):
        """Test AI service streaming with mocked API."""
        with patch("src.bot.services.ai_service.AsyncOpenAI") as mock_openai_class:
            mock_client = AsyncMock()
            mock_openai_class.return_value = mock_client

            # Setup streaming response
            async def mock_stream():
                chunks = ["Good", " day", ", Sir.", " How", " may", " I", " help?"]
                for chunk_text in chunks:
                    mock_chunk = MagicMock()
                    mock_chunk.choices = [MagicMock()]
                    mock_chunk.choices[0].delta.content = chunk_text
                    yield mock_chunk

            mock_client.chat.completions.create = AsyncMock(
                return_value=mock_stream(),
            )

            service = OpenAIService(JARVIS_PERSONA_V1)
            user_context = {
                "user_id": 123456789,
                "recent_transactions": [],
            }

            response_stream = await service.generate_response(
                "Hello",
                user_context,
                stream=True,
            )

            # Collect streamed content
            content = ""
            async for chunk in response_stream:
                content += chunk

            assert len(content) > 0
            assert "Good" in content or "Sir" in content

