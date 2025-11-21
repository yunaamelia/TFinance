"""Unit tests for AI chat handler error cases."""

from unittest.mock import MagicMock

import pytest
from telegram import Chat, Message, Update
from telegram import User as TelegramUser

from src.bot.handlers.ai_chat import cancel_ai_chat, handle_ai_message
from src.bot.utils.errors import AIServiceError


class TestAIChatErrorCases:
    """Test AI chat handler error cases."""

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
            text="Hello",
        )
        update = Update(update_id=1, message=message)
        return update

    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        context = MagicMock()
        context.user_data = {}
        context.bot.send_chat_action = MagicMock()
        return context

    @pytest.mark.asyncio
    async def test_handle_ai_message_no_message(self, mock_update, mock_context, mocker):
        """Test handle_ai_message when update has no message."""
        # Create update without message
        from telegram import Update

        update_no_message = Update(update_id=2)

        result = await handle_ai_message(update_no_message, mock_context)

        # Should return AI_CHAT state
        from src.bot.handlers.ai_chat import AI_CHAT

        assert result == AI_CHAT

    @pytest.mark.asyncio
    async def test_handle_ai_message_no_text(self, mock_update, mock_context, mocker):
        """Test handle_ai_message when message has no text."""
        # Set message text to None
        object.__setattr__(mock_update.message, "text", None)

        result = await handle_ai_message(mock_update, mock_context)

        # Should return AI_CHAT state
        from src.bot.handlers.ai_chat import AI_CHAT

        assert result == AI_CHAT

    @pytest.mark.asyncio
    async def test_handle_ai_message_processing_fails(self, mock_update, mock_context, mocker):
        """Test handle_ai_message when processing message fails."""
        # Mock AI service
        mock_ai_service = mocker.MagicMock()
        mock_ai_service.generate_response = mocker.AsyncMock(
            return_value="Response",
        )
        mocker.patch(
            "src.bot.handlers.ai_chat.get_ai_service",
            return_value=mock_ai_service,
        )

        # Mock database session
        mock_db_session = mocker.AsyncMock()
        mock_session_maker = mocker.MagicMock()
        mock_session_maker.return_value.__aenter__ = mocker.AsyncMock(return_value=mock_db_session)
        mock_session_maker.return_value.__aexit__ = mocker.AsyncMock(return_value=None)
        mocker.patch(
            "src.bot.handlers.ai_chat.get_async_session_maker",
            return_value=mock_session_maker,
        )

        # Mock User query
        from src.bot.models.user import User

        mock_user = User(id=123456789, first_name="Test")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute = mocker.AsyncMock(return_value=mock_result)

        # Mock TransactionService
        mock_transaction_service = mocker.AsyncMock()
        mock_transaction_service.get_transactions = mocker.AsyncMock(return_value=[])
        mocker.patch(
            "src.bot.handlers.ai_chat.TransactionService",
            return_value=mock_transaction_service,
        )

        # Mock reply_text to fail
        reply_text_mock = mocker.AsyncMock(side_effect=Exception("Send failed"))
        mocker.patch(
            "telegram.Update.message",
            new_callable=mocker.PropertyMock,
            return_value=MagicMock(reply_text=reply_text_mock),
        )

        result = await handle_ai_message(mock_update, mock_context)

        # Should still return AI_CHAT state
        from src.bot.handlers.ai_chat import AI_CHAT

        assert result == AI_CHAT

    @pytest.mark.asyncio
    async def test_handle_ai_message_edit_fails(self, mock_update, mock_context, mocker):
        """Test handle_ai_message when editing processing message fails."""
        # Mock AI service
        mock_ai_service = mocker.MagicMock()
        mock_ai_service.generate_response = mocker.AsyncMock(
            return_value="Response",
        )
        mocker.patch(
            "src.bot.handlers.ai_chat.get_ai_service",
            return_value=mock_ai_service,
        )

        # Mock database session
        mock_db_session = mocker.AsyncMock()
        mock_session_maker = mocker.MagicMock()
        mock_session_maker.return_value.__aenter__ = mocker.AsyncMock(return_value=mock_db_session)
        mock_session_maker.return_value.__aexit__ = mocker.AsyncMock(return_value=None)
        mocker.patch(
            "src.bot.handlers.ai_chat.get_async_session_maker",
            return_value=mock_session_maker,
        )

        # Mock User query
        from src.bot.models.user import User

        mock_user = User(id=123456789, first_name="Test")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute = mocker.AsyncMock(return_value=mock_result)

        # Mock TransactionService
        mock_transaction_service = mocker.AsyncMock()
        mock_transaction_service.get_transactions = mocker.AsyncMock(return_value=[])
        mocker.patch(
            "src.bot.handlers.ai_chat.TransactionService",
            return_value=mock_transaction_service,
        )

        # Mock processing message - edit fails, delete fails, but new message succeeds
        mock_processing_msg = MagicMock()
        mock_processing_msg.edit_text = mocker.AsyncMock(side_effect=Exception("Edit failed"))
        mock_processing_msg.delete = mocker.AsyncMock(side_effect=Exception("Delete failed"))

        # Mock reply_text for new message (second call)
        mock_new_message = MagicMock()
        reply_text_mock = mocker.AsyncMock(
            side_effect=[
                mock_processing_msg,  # First call returns processing message
                mock_new_message,  # Second call returns new message
            ]
        )
        mocker.patch(
            "telegram.Update.message",
            new_callable=mocker.PropertyMock,
            return_value=MagicMock(reply_text=reply_text_mock),
        )

        result = await handle_ai_message(mock_update, mock_context)

        # Should still return AI_CHAT state
        from src.bot.handlers.ai_chat import AI_CHAT

        assert result == AI_CHAT

    @pytest.mark.asyncio
    async def test_handle_ai_message_ai_error_edit_fails(self, mock_update, mock_context, mocker):
        """Test handle_ai_message when AI error occurs and edit fails."""
        # Mock AI service to raise error
        mock_ai_service = mocker.MagicMock()
        mock_ai_service.generate_response = mocker.AsyncMock(
            side_effect=AIServiceError("Service unavailable", status_code=503),
        )
        mocker.patch(
            "src.bot.handlers.ai_chat.get_ai_service",
            return_value=mock_ai_service,
        )

        # Mock database session
        mock_db_session = mocker.AsyncMock()
        mock_session_maker = mocker.MagicMock()
        mock_session_maker.return_value.__aenter__ = mocker.AsyncMock(return_value=mock_db_session)
        mock_session_maker.return_value.__aexit__ = mocker.AsyncMock(return_value=None)
        mocker.patch(
            "src.bot.handlers.ai_chat.get_async_session_maker",
            return_value=mock_session_maker,
        )

        # Mock User query
        from src.bot.models.user import User

        mock_user = User(id=123456789, first_name="Test")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute = mocker.AsyncMock(return_value=mock_result)

        # Mock TransactionService
        mock_transaction_service = mocker.AsyncMock()
        mock_transaction_service.get_transactions = mocker.AsyncMock(return_value=[])
        mocker.patch(
            "src.bot.handlers.ai_chat.TransactionService",
            return_value=mock_transaction_service,
        )

        # Mock processing message - edit fails, delete fails, but new message succeeds
        mock_processing_msg = MagicMock()
        mock_processing_msg.edit_text = mocker.AsyncMock(side_effect=Exception("Edit failed"))
        mock_processing_msg.delete = mocker.AsyncMock(side_effect=Exception("Delete failed"))
        mocker.patch.object(
            mock_update.message,
            "reply_text",
            new=mocker.AsyncMock(
                side_effect=[
                    mock_processing_msg,  # First call returns processing message
                    MagicMock(),  # Second call returns new message
                ]
            ),
        )

        result = await handle_ai_message(mock_update, mock_context)

        # Should still return AI_CHAT state
        from src.bot.handlers.ai_chat import AI_CHAT

        assert result == AI_CHAT

    @pytest.mark.asyncio
    async def test_cancel_ai_chat_callback_query(self, mock_update, mock_context, mocker):
        """Test cancel_ai_chat with callback query."""
        from telegram import CallbackQuery

        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.edit_message_text = mocker.AsyncMock()
        object.__setattr__(mock_update, "callback_query", callback_query)
        object.__setattr__(mock_update, "message", None)

        result = await cancel_ai_chat(mock_update, mock_context)

        # Should return ConversationHandler.END
        from telegram.ext import ConversationHandler

        assert result == ConversationHandler.END
        callback_query.edit_message_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_cancel_ai_chat_message(self, mock_update, mock_context, mocker):
        """Test cancel_ai_chat with message."""
        reply_text_mock = mocker.AsyncMock()
        mocker.patch(
            "telegram.Update.message",
            new_callable=mocker.PropertyMock,
            return_value=MagicMock(reply_text=reply_text_mock),
        )

        result = await cancel_ai_chat(mock_update, mock_context)

        # Should return ConversationHandler.END
        from telegram.ext import ConversationHandler

        assert result == ConversationHandler.END
        mock_update.message.reply_text.assert_called_once()
