#!/bin/bash
# Comprehensive bot debugging script

echo "🔍 FinancialAssist Bot Debugging"
echo "=================================="
echo ""

cd "$(dirname "$0")/.." || exit 1

echo "1. Checking bot process..."
if ps aux | grep "python -m src.bot.main" | grep -v grep | grep -v bash > /dev/null; then
    echo "   ✅ Bot is running"
    ./scripts/check_bot_status.sh
else
    echo "   ❌ Bot is NOT running"
    echo "   Start with: python -m src.bot.main"
    exit 1
fi

echo ""
echo "2. Testing bot connection..."
python scripts/test_bot_response.py 2>&1 | grep -E "(✅|❌|Bot:|commands)" || echo "   ⚠️  Connection test failed (may be flood control)"

echo ""
echo "3. Checking recent logs for errors..."
if [ -f /tmp/bot_debug_full.log ]; then
    echo "   Recent errors:"
    tail -50 /tmp/bot_debug_full.log | grep -E "(ERROR|Exception|Failed|❌)" | tail -5 || echo "   ✅ No recent errors"

    echo ""
    echo "   Recent updates received:"
    tail -50 /tmp/bot_debug_full.log | grep -E "(Received|📨|🔘|start)" | tail -5 || echo "   ⚠️  No updates logged yet"
else
    echo "   ⚠️  No log file found"
fi

echo ""
echo "4. Checking database connection..."
python -c "
import asyncio
from src.bot.config.settings import get_async_session_maker
from sqlalchemy import text

async def test():
    try:
        session_maker = get_async_session_maker()
        async with session_maker() as session:
            await session.execute(text('SELECT 1'))
        print('   ✅ Database connected')
    except Exception as e:
        print(f'   ❌ Database error: {e}')

asyncio.run(test())
" 2>&1

echo ""
echo "5. Checking Redis connection..."
python -c "
import asyncio
from src.bot.config.settings import get_redis_client

async def test():
    try:
        redis = await get_redis_client()
        await redis.ping()
        print('   ✅ Redis connected')
    except Exception as e:
        print(f'   ❌ Redis error: {e}')

asyncio.run(test())
" 2>&1

echo ""
echo "=================================="
echo "💡 Next steps:"
echo "   1. Send /start to @AIPembukuanbot in Telegram"
echo "   2. Monitor logs: tail -f /tmp/bot_debug_full.log"
echo "   3. Check for errors in the output above"
echo ""
