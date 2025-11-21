"""Integration tests for transaction recording flow."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram import Chat, Message, Update
from telegram import User as TelegramUser
from telegram.ext import ContextTypes

from src.bot.handlers.transaction import (
    TRANSACTION_AMOUNT,
    TRANSACTION_CATEGORY,
    handle_transaction_amount,
    handle_transaction_type,
)


class TestTransactionFlow:
    """Test transaction recording conversation flow."""

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
    @patch("src.bot.handlers.transaction.get_redis_client")
    async def test_transaction_type_selection_income(
        self, mock_get_redis, mock_update, mock_context
    ):
        """Test selecting income transaction type."""
        from telegram import CallbackQuery

        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.answer = AsyncMock()
        callback_query.edit_message_text = AsyncMock()
        callback_query.from_user = mock_update.effective_user
        callback_query.data = "transaction_type:income"

        object.__setattr__(mock_update, "callback_query", callback_query)

        # Mock Redis
        mock_redis = AsyncMock()
        mock_get_redis.return_value = mock_redis

        result = await handle_transaction_type(mock_update, mock_context)

        assert result == TRANSACTION_AMOUNT
        assert mock_context.user_data["transaction_type"] == "income"
        callback_query.edit_message_text.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.bot.handlers.transaction.get_redis_client")
    async def test_transaction_type_selection_expense(
        self, mock_get_redis, mock_update, mock_context
    ):
        """Test selecting expense transaction type."""
        from telegram import CallbackQuery

        callback_query = MagicMock(spec=CallbackQuery)
        callback_query.answer = AsyncMock()
        callback_query.edit_message_text = AsyncMock()
        callback_query.from_user = mock_update.effective_user
        callback_query.data = "transaction_type:expense"

        object.__setattr__(mock_update, "callback_query", callback_query)

        # Mock Redis
        mock_redis = AsyncMock()
        mock_get_redis.return_value = mock_redis

        result = await handle_transaction_type(mock_update, mock_context)

        assert result == TRANSACTION_AMOUNT
        assert mock_context.user_data["transaction_type"] == "expense"

    @pytest.mark.asyncio
    async def test_transaction_amount_valid(self, mock_update, mock_context):
        """Test valid amount input."""
        mock_context.user_data["transaction_type"] = "expense"

        # Create a mock message with reply_text
        mock_message = MagicMock(spec=Message)
        mock_message.text = "50000"
        mock_message.reply_text = AsyncMock()
        mock_message.chat = mock_update.message.chat
        mock_message.from_user = mock_update.message.from_user
        object.__setattr__(mock_update, "message", mock_message)

        result = await handle_transaction_amount(mock_update, mock_context)

        assert result == TRANSACTION_CATEGORY
        assert "amount" in mock_context.user_data
        mock_message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_transaction_amount_invalid(self, mock_update, mock_context):
        """Test invalid amount input."""
        mock_context.user_data["transaction_type"] = "expense"

        # Create a mock message with reply_text
        mock_message = MagicMock(spec=Message)
        mock_message.text = "invalid"
        mock_message.reply_text = AsyncMock()
        mock_message.chat = mock_update.message.chat
        mock_message.from_user = mock_update.message.from_user
        object.__setattr__(mock_update, "message", mock_message)

        result = await handle_transaction_amount(mock_update, mock_context)

        # Should stay in same state on error
        assert result == TRANSACTION_AMOUNT
        mock_message.reply_text.assert_called()
