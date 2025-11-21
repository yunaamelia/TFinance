"""Summary service for calculating financial summaries."""

import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal

import redis.asyncio as redis
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.config.settings import settings
from src.bot.models.transaction import Transaction
from src.bot.utils.errors import DatabaseError

logger = logging.getLogger(__name__)


class SummaryService:
    """Service for financial summary calculations."""

    def __init__(self, session: AsyncSession, redis_client: redis.Redis):
        """Initialize SummaryService.

        Args:
            session: Async database session
            redis_client: Redis client for caching
        """
        self.session = session
        self.redis = redis_client
        self.cache_ttl = settings.cache_ttl  # 5 minutes default

    def _get_period_dates(self, period: str) -> tuple[datetime, datetime]:
        """Calculate start and end dates for a time period.

        Args:
            period: Time period ("today", "week", "month", "custom")

        Returns:
            Tuple of (start_date, end_date)
        """
        now = datetime.now()
        end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        if period == "today":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            start_date = (now - timedelta(days=6)).replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
        elif period == "month":
            start_date = (now - timedelta(days=30)).replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
        else:
            # Default to month
            start_date = (now - timedelta(days=30)).replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )

        return start_date, end_date

    def _calculate_summary(
        self,
        user_id: int,
        transactions: list[Transaction],
        period: str,
    ) -> dict:
        """Calculate financial summary from transactions.

        Args:
            user_id: User ID
            transactions: List of Transaction objects
            period: Time period

        Returns:
            Dictionary with summary data
        """
        start_date, end_date = self._get_period_dates(period)

        total_income = Decimal("0.00")
        total_expenses = Decimal("0.00")

        for transaction in transactions:
            if transaction.type == "income":
                total_income += transaction.amount
            elif transaction.type == "expense":
                total_expenses += transaction.amount

        net_balance = total_income - total_expenses
        category_breakdown = self._get_category_breakdown(transactions)

        return {
            "user_id": user_id,
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_balance": net_balance,
            "transaction_count": len(transactions),
            "category_breakdown": category_breakdown,
        }

    def _get_category_breakdown(self, transactions: list[Transaction]) -> dict[str, Decimal]:
        """Get expenses grouped by category.

        Args:
            transactions: List of Transaction objects

        Returns:
            Dictionary mapping category names to total amounts
        """
        breakdown = {}

        for transaction in transactions:
            if transaction.type == "expense":
                category = transaction.category
                if category not in breakdown:
                    breakdown[category] = Decimal("0.00")
                breakdown[category] += transaction.amount

        return breakdown

    async def get_financial_summary(
        self,
        user_id: int,
        period: str = "month",
    ) -> dict:
        """Get financial summary for a time period.

        Args:
            user_id: User ID
            period: Time period ("today", "week", "month", "custom")

        Returns:
            Dictionary with financial summary data

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            # Check cache first
            cache_key = f"summary:{user_id}:{period}"
            if self.redis:
                cached_data = await self.redis.get(cache_key)
                if cached_data:
                    logger.debug(f"Cache hit for {cache_key}")
                    return json.loads(cached_data)

            # Calculate dates
            start_date, end_date = self._get_period_dates(period)

            # Query transactions
            query = select(Transaction).where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.timestamp >= start_date,
                    Transaction.timestamp <= end_date,
                    Transaction.deleted_at.is_(None),
                ),
            )

            result = await self.session.execute(query)
            transactions = result.scalars().all()

            # Calculate summary
            summary = self._calculate_summary(user_id, list(transactions), period)

            # Convert Decimal to float for JSON serialization
            summary_json = {
                "user_id": summary["user_id"],
                "period": summary["period"],
                "start_date": summary["start_date"].isoformat(),
                "end_date": summary["end_date"].isoformat(),
                "total_income": float(summary["total_income"]),
                "total_expenses": float(summary["total_expenses"]),
                "net_balance": float(summary["net_balance"]),
                "transaction_count": summary["transaction_count"],
                "category_breakdown": {
                    k: float(v) for k, v in summary["category_breakdown"].items()
                },
            }

            # Cache result
            if self.redis:
                await self.redis.set(
                    cache_key,
                    json.dumps(summary_json),
                    ex=self.cache_ttl,
                )
                logger.debug(f"Cached summary for {cache_key}")

            # Convert back to Decimal for return
            summary["total_income"] = Decimal(str(summary_json["total_income"]))
            summary["total_expenses"] = Decimal(str(summary_json["total_expenses"]))
            summary["net_balance"] = Decimal(str(summary_json["net_balance"]))
            summary["category_breakdown"] = {
                k: Decimal(str(v)) for k, v in summary_json["category_breakdown"].items()
            }

            return summary

        except Exception as e:
            logger.error(f"Error getting financial summary: {e}", exc_info=True)
            raise DatabaseError(
                f"Failed to get financial summary: {str(e)}",
                operation="get_financial_summary",
            ) from e

    async def get_category_breakdown(
        self,
        user_id: int,
        period: str = "month",
    ) -> dict[str, Decimal]:
        """Get expenses grouped by category.

        Args:
            user_id: User ID
            period: Time period

        Returns:
            Dictionary mapping category names to amounts

        Raises:
            DatabaseError: If database operation fails
        """
        try:
            summary = await self.get_financial_summary(user_id, period)
            return summary.get("category_breakdown", {})

        except DatabaseError:
            raise
        except Exception as e:
            logger.error(f"Error getting category breakdown: {e}", exc_info=True)
            raise DatabaseError(
                f"Failed to get category breakdown: {str(e)}",
                operation="get_category_breakdown",
            ) from e

    async def invalidate_cache(self, user_id: int):
        """Invalidate cached summaries for a user.

        Args:
            user_id: User ID
        """
        if self.redis:
            # Invalidate all period caches for this user
            periods = ["today", "week", "month"]
            for period in periods:
                cache_key = f"summary:{user_id}:{period}"
                await self.redis.delete(cache_key)
            logger.debug(f"Invalidated cache for user {user_id}")
