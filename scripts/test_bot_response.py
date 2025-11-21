#!/usr/bin/env python3
"""Test script to verify bot is responding."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from telegram import Bot

from src.bot.config.settings import settings


async def test_bot():
    """Test bot connection and response."""
    print("🧪 Testing Bot Response...")
    print("=" * 60)

    bot = Bot(token=settings.telegram_bot_token)

    try:
        # Test 1: Get bot info
        print("\n1. Testing bot connection...")
        me = await bot.get_me()
        print(f"   ✅ Bot: @{me.username} ({me.first_name})")
        print(f"   ✅ Bot ID: {me.id}")

        # Test 2: Get recent updates
        print("\n2. Checking for recent updates...")
        updates = await bot.get_updates(limit=5, timeout=5)
        print(f"   ✅ Found {len(updates)} recent updates")
        if updates:
            print(f"   ✅ Last update ID: {updates[-1].update_id}")
            print("   ✅ Bot is receiving updates from Telegram")
        else:
            print("   ⚠️  No recent updates. This is normal if bot just started.")

        # Test 3: Check bot commands
        print("\n3. Checking bot commands...")
        commands = await bot.get_my_commands()
        print(f"   ✅ Bot has {len(commands)} commands registered:")
        for cmd in commands:
            print(f"      /{cmd.command} - {cmd.description}")

        print("\n" + "=" * 60)
        print("✅ All tests passed! Bot should be working.")
        print("\n💡 If bot is not responding:")
        print("   1. Make sure bot is running: ./scripts/check_bot_status.sh")
        print("   2. Check logs: tail -f /tmp/bot_debug_full.log")
        print("   3. Try sending /start to bot in Telegram")
        print(f"   4. Check if you're sending to the correct bot: @{me.username}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        await bot.close()

    return True


if __name__ == "__main__":
    asyncio.run(test_bot())
