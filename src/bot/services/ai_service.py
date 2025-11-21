"""AI service for generating responses with JARVIS persona."""

import logging
from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, List, Optional

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from src.bot.config.persona import build_jarvis_prompt
from src.bot.config.settings import settings
from src.bot.models.transaction import Transaction
from src.bot.utils.errors import AIServiceError
from src.bot.utils.formatters import format_currency

logger = logging.getLogger(__name__)


class AIService(ABC):
    """Abstract base class for AI services."""

    @abstractmethod
    async def generate_response(
        self,
        user_message: str,
        user_context: dict,
        stream: bool = False,
    ) -> AsyncIterator[str] | str:
        """Generate AI response with JARVIS persona.

        Args:
            user_message: User's message/query
            user_context: User context data
                - user_id (int): User ID
                - recent_transactions (List[Transaction]): Recent transactions
                - financial_summary (dict, optional): Current financial summary
                - conversation_history (List[dict], optional): Previous messages
            stream: Whether to stream response (default: False)

        Returns:
            If stream=True: AsyncIterator[str] (token stream)
            If stream=False: str (complete response)

        Raises:
            AIServiceError: If AI API call fails
        """
        pass

    @abstractmethod
    async def analyze_spending_pattern(
        self,
        user_id: int,
        period: str,
    ) -> dict:
        """Analyze user's spending patterns.

        Args:
            user_id: User ID
            period: Time period ("today", "week", "month")

        Returns:
            Analysis dictionary with top_categories, trends, recommendations

        Raises:
            AIServiceError: If analysis fails
        """
        pass


class OpenAIService(AIService):
    """OpenAI implementation of AIService."""

    def __init__(self, persona_config: dict = None):
        """Initialize OpenAI service.

        Args:
            persona_config: Persona configuration dictionary
        """
        self.persona_config = persona_config or {}
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-4o-mini"  # Use cost-effective model

    def _build_context_summary(self, user_context: dict) -> str:
        """Build context summary string from user context.

        Args:
            user_context: User context dictionary

        Returns:
            str: Formatted context summary
        """
        user_id = user_context.get("user_id", "Unknown")
        transactions = user_context.get("recent_transactions", [])
        financial_summary = user_context.get("financial_summary")

        summary_parts = [f"User ID: {user_id}"]

        if transactions:
            summary_parts.append(f"Recent transactions: {len(transactions)}")
            # Summarize recent transactions
            income_total = sum(
                t.amount for t in transactions if t.type == "income"
            )
            expense_total = sum(
                t.amount for t in transactions if t.type == "expense"
            )
            if income_total > 0:
                summary_parts.append(
                    f"Recent income: {format_currency(income_total)}",
                )
            if expense_total > 0:
                summary_parts.append(
                    f"Recent expenses: {format_currency(expense_total)}",
                )

        if financial_summary:
            net_balance = financial_summary.get("net_balance", 0)
            summary_parts.append(f"Current balance: {format_currency(net_balance)}")

        return "\n".join(summary_parts)

    def _build_recent_transactions_summary(
        self,
        transactions: List[Transaction],
    ) -> str:
        """Build summary of recent transactions.

        Args:
            transactions: List of Transaction objects

        Returns:
            str: Formatted transactions summary
        """
        if not transactions:
            return "No recent transactions."

        lines = []
        for transaction in transactions[:10]:  # Limit to 10 most recent
            type_emoji = "💰" if transaction.type == "income" else "💸"
            lines.append(
                f"{type_emoji} {transaction.type}: {format_currency(transaction.amount)} "
                f"- {transaction.category}",
            )

        return "\n".join(lines)

    def _build_financial_summary_string(self, financial_summary: dict) -> str:
        """Build financial summary string.

        Args:
            financial_summary: Financial summary dictionary

        Returns:
            str: Formatted financial summary
        """
        if not financial_summary:
            return "No financial summary available."

        parts = []
        if "total_income" in financial_summary:
            parts.append(
                f"Total Income: {format_currency(financial_summary['total_income'])}",
            )
        if "total_expenses" in financial_summary:
            parts.append(
                f"Total Expenses: {format_currency(financial_summary['total_expenses'])}",
            )
        if "net_balance" in financial_summary:
            parts.append(
                f"Net Balance: {format_currency(financial_summary['net_balance'])}",
            )

        return "\n".join(parts) if parts else "No financial data available."

    def _build_system_prompt(self, user_context: dict) -> str:
        """Build JARVIS system prompt with user context.

        Args:
            user_context: User context dictionary

        Returns:
            str: Complete system prompt
        """
        context_summary = self._build_context_summary(user_context)
        transactions = user_context.get("recent_transactions", [])
        recent_transactions = self._build_recent_transactions_summary(transactions)
        financial_summary = user_context.get("financial_summary", {})
        financial_summary_str = self._build_financial_summary_string(financial_summary)

        return build_jarvis_prompt(
            context_summary=context_summary,
            recent_transactions=recent_transactions,
            financial_summary=financial_summary_str,
        )

    async def generate_response(
        self,
        user_message: str,
        user_context: dict,
        stream: bool = False,
    ) -> AsyncIterator[str] | str:
        """Generate AI response with JARVIS persona.

        Args:
            user_message: User's message/query
            user_context: User context data
            stream: Whether to stream response

        Returns:
            If stream=True: AsyncIterator[str]
            If stream=False: str

        Raises:
            AIServiceError: If AI API call fails
        """
        try:
            system_prompt = self._build_system_prompt(user_context)

            # Build conversation history
            conversation_history = user_context.get("conversation_history", [])
            messages: List[ChatCompletionMessageParam] = [
                {"role": "system", "content": system_prompt},
            ]

            # Add conversation history (last 10 messages)
            for msg in conversation_history[-10:]:
                messages.append(msg)

            # Add current user message
            messages.append({"role": "user", "content": user_message})

            if stream:
                # Stream response
                async def stream_generator():
                    async for chunk in await self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        stream=True,
                        temperature=0.7,
                        max_tokens=500,
                    ):
                        if chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content

                return stream_generator()
            else:
                # Get complete response
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500,
                )
                return response.choices[0].message.content or ""

        except Exception as e:
            logger.error(f"AI service error: {e}", exc_info=True)
            raise AIServiceError(
                f"Failed to generate AI response: {str(e)}",
                status_code=getattr(e, "status_code", None),
            ) from e

    async def analyze_spending_pattern(
        self,
        user_id: int,
        period: str,
    ) -> dict:
        """Analyze user's spending patterns.

        Args:
            user_id: User ID
            period: Time period ("today", "week", "month")

        Returns:
            Analysis dictionary with top_categories, trends, recommendations

        Raises:
            AIServiceError: If analysis fails
        """
        # This would typically use the AI to analyze spending patterns
        # For now, return a basic structure that can be enhanced
        try:
            # TODO: Implement actual spending pattern analysis using AI
            # This would query transactions and use AI to identify patterns
            return {
                "top_categories": [],
                "trends": {},
                "recommendations": [],
            }
        except Exception as e:
            logger.error(f"Spending pattern analysis error: {e}", exc_info=True)
            raise AIServiceError(
                f"Failed to analyze spending patterns: {str(e)}",
            ) from e

