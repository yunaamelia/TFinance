"""Health check handler for monitoring."""

import logging
import time
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.config.settings import get_async_session_maker, get_redis_client, settings

logger = logging.getLogger(__name__)

# Track bot start time for uptime calculation
_start_time = time.time()


async def health_check_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /health command for monitoring.

    Args:
        update: Telegram update
        context: Bot context
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": int(time.time() - _start_time),
        "environment": settings.environment,
        "checks": {},
    }

    # Check database connection
    try:
        async_session_maker = get_async_session_maker()
        async with async_session_maker() as session:
            await session.execute("SELECT 1")
        health_status["checks"]["database"] = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["checks"]["database"] = "disconnected"
        health_status["status"] = "degraded"

    # Check Redis connection
    try:
        redis_client = await get_redis_client()
        await redis_client.ping()
        health_status["checks"]["redis"] = "connected"
    except Exception as e:
        logger.warning(f"Redis health check failed: {e}")
        health_status["checks"]["redis"] = "disconnected"
        # Redis is optional, don't mark as degraded

    # Format health status message
    status_emoji = "✅" if health_status["status"] == "healthy" else "⚠️"
    message = f"{status_emoji} *Health Check*\n\n"
    message += f"Status: {health_status['status'].upper()}\n"
    message += f"Uptime: {health_status['uptime_seconds']} seconds\n"
    message += f"Environment: {health_status['environment']}\n\n"
    message += "*Checks:*\n"
    for check, status in health_status["checks"].items():
        emoji = "✅" if status == "connected" else "❌"
        message += f"{emoji} {check.capitalize()}: {status}\n"

    if update.effective_message:
        await update.effective_message.reply_text(message, parse_mode="Markdown")


def get_health_status() -> dict:
    """Get current health status (for API/webhook endpoints).

    Returns:
        Dictionary with health status information
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": int(time.time() - _start_time),
        "environment": settings.environment,
    }
