"""Integration tests for edge cases and error handling."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram import Chat, Message, Update
from telegram import User as TelegramUser
from telegram.ext import ContextTypes

from src.bot.handlers.ai_chat import handle_ai_message
from src.bot.handlers.transaction import handle_transaction_amount
from src.bot.utils.errors import AIServiceError, DatabaseError, ValidationError


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def mock_update(self):
        """Create mock Telegram update."""
        telegram_user = TelegramUser(
            id=123456789,
            first_name="Test",
            is_bot=False,
        )
        chat = Chat(id=123456789, type="private")
        message = Message(
            message_id=1,
            date=None,
            chat=chat,
            from_user=telegram_user,
        )
        update = Update(update_id=1, message=message)
        return update

    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        return context

    @pytest.mark.asyncio
    async def test_invalid_amount_input(self, mock_update, mock_context):
        """Test handling of invalid amount input."""
        mock_context.user_data["transaction_type"] = "expense"

        # Create mock message
        mock_message = MagicMock(spec=Message)
        mock_message.text = "not_a_number"
        mock_message.reply_text = AsyncMock()
        mock_message.chat = mock_update.message.chat
        mock_message.from_user = mock_update.message.from_user
        object.__setattr__(mock_update, "message", mock_message)

        result = await handle_transaction_amount(mock_update, mock_context)

        # Should stay in same state and show error
        assert result is not None  # Should return TRANSACTION_AMOUNT state
        mock_message.reply_text.assert_called()

    @pytest.mark.asyncio
    async def test_negative_amount_input(self, mock_update, mock_context):
        """Test handling of negative amount input."""
        mock_context.user_data["transaction_type"] = "expense"

        mock_message = MagicMock(spec=Message)
        mock_message.text = "-50000"
        mock_message.reply_text = AsyncMock()
        mock_message.chat = mock_update.message.chat
        mock_message.from_user = mock_update.message.from_user
        object.__setattr__(mock_update, "message", mock_message)

        result = await handle_transaction_amount(mock_update, mock_context)

        # Should show validation error
        assert result is not None
        mock_message.reply_text.assert_called()

    @pytest.mark.asyncio
    @patch("src.bot.handlers.ai_chat.get_ai_service")
    @patch("src.bot.handlers.ai_chat.get_async_session_maker")
    @patch("src.bot.handlers.ai_chat.get_redis_client")
    @patch("src.bot.handlers.ai_chat.TransactionService")
    async def test_ai_service_failure(
        self,
        mock_transaction_service,
        mock_redis,
        mock_session,
        mock_get_service,
        mock_update,
        mock_context,
    ):
        """Test handling of AI service failure."""
        # Mock AI service to raise error
        mock_ai_service = AsyncMock()
        mock_ai_service.generate_response = AsyncMock(
            side_effect=AIServiceError("AI service unavailable", status_code=503)
        )
        mock_get_service.return_value = mock_ai_service

        # Mock database and Redis
        mock_db_session = AsyncMock()
        mock_session.return_value.__aenter__.return_value = mock_db_session
        mock_session.return_value.__aexit__.return_value = None

        mock_transaction_service_instance = AsyncMock()
        mock_transaction_service_instance.get_transactions = AsyncMock(return_value=[])
        mock_transaction_service.return_value = mock_transaction_service_instance

        mock_redis.return_value = AsyncMock()

        # Create mock message
        mock_message = MagicMock(spec=Message)
        mock_message.text = "What is my balance?"
        mock_message.reply_text = AsyncMock()
        mock_message.chat = mock_update.message.chat
        mock_message.from_user = mock_update.message.from_user
        object.__setattr__(mock_update, "message", mock_message)

        # Mock context.bot.send_chat_action
        mock_context.bot = MagicMock()
        mock_context.bot.send_chat_action = AsyncMock()

        # Mock processing message (returned by reply_text)
        mock_processing_msg = MagicMock()
        mock_processing_msg.edit_text = AsyncMock()
        mock_processing_msg.delete = AsyncMock()
        mock_message.reply_text.return_value = mock_processing_msg

        # Mock User model query
        mock_user_result = MagicMock()
        mock_user_result.scalar_one_or_none = AsyncMock(return_value=None)  # User doesn't exist
        mock_db_session.execute = AsyncMock(return_value=mock_user_result)
        # Also mock commit for user creation
        mock_db_session.commit = AsyncMock()

        # Mock get_redis_client
        async def get_redis_mock():
            return AsyncMock()

        mock_redis.side_effect = get_redis_mock

        # Should handle error gracefully
        await handle_ai_message(mock_update, mock_context)

        # Error message should be sent to user (either via edit_text or reply_text)
        # Check if processing message was edited with error or new message was sent
        if mock_processing_msg.edit_text.called:
            call_args = mock_processing_msg.edit_text.call_args[0][0]
            assert any(
                word in call_args.lower()
                for word in ["unavailable", "error", "difficulties", "try again"]
            )
        else:
            mock_message.reply_text.assert_called()
            call_args = mock_message.reply_text.call_args[0][0]
            assert any(
                word in call_args.lower()
                for word in ["unavailable", "error", "difficulties", "try again"]
            )

    @pytest.mark.asyncio
    @patch("src.bot.handlers.transaction.get_async_session_maker")
    async def test_database_error_handling(self, mock_session, mock_update, mock_context):
        """Test handling of database errors."""
        mock_context.user_data["transaction_type"] = "expense"

        mock_message = MagicMock(spec=Message)
        mock_message.text = "50000"
        mock_message.reply_text = AsyncMock()
        mock_message.chat = mock_update.message.chat
        mock_message.from_user = mock_update.message.from_user
        object.__setattr__(mock_update, "message", mock_message)

        # Mock database session to raise error when executing query
        mock_db_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []  # Empty categories list
        mock_db_session.execute = AsyncMock(
            side_effect=DatabaseError("Database connection failed", operation="query")
        )
        mock_session.return_value.__aenter__.return_value = mock_db_session
        mock_session.return_value.__aexit__.return_value = None

        # Should handle database error gracefully
        # The handler should catch the error and show error message to user
        result = await handle_transaction_amount(mock_update, mock_context)

        # Should return to same state (TRANSACTION_AMOUNT) and show error
        assert result is not None
        # Error message should be sent to user
        mock_message.reply_text.assert_called()

    @pytest.mark.asyncio
    async def test_empty_category_input(self, mock_update, mock_context):
        """Test handling of empty category input."""
        # This would be tested in category handler
        # For now, verify validator rejects empty category
        from src.bot.utils.validators import validate_category

        with pytest.raises(ValidationError, match="1-100 characters"):
            validate_category("", "expense")

    @pytest.mark.asyncio
    async def test_very_long_input(self, mock_update, mock_context):
        """Test handling of very long input."""
        from src.bot.utils.validators import validate_category

        # Test category that's too long
        long_category = "A" * 101
        with pytest.raises(ValidationError, match="1-100 characters"):
            validate_category(long_category, "expense")
