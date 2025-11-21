#!/usr/bin/env python3
"""Script to setup Telegram bot commands via Bot API."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from telegram import Bot, BotCommand
from telegram.error import TelegramError

from src.bot.config.settings import settings
from src.bot.utils.telegram_helpers import handle_telegram_retry_after


async def setup_commands():
    """Set up bot commands via Telegram Bot API."""
    bot = Bot(token=settings.telegram_bot_token)

    commands = [
        BotCommand("start", "Mulai bot dan tampilkan menu utama"),
        BotCommand("health", "Cek status bot, database, dan Redis"),
    ]

    try:
        # Use retry helper to handle flood control automatically
        await handle_telegram_retry_after(bot.set_my_commands, commands)
        print("✅ Bot commands berhasil dikonfigurasi!")
        print("\nCommands yang diatur:")
        for cmd in commands:
            print(f"  /{cmd.command} - {cmd.description}")

        # Wait before next request to avoid flood control
        await asyncio.sleep(1)

        # Verify with retry handling
        my_commands = await handle_telegram_retry_after(bot.get_my_commands)
        print(f"\n✅ Verifikasi: {len(my_commands)} commands terdaftar")

        return True

    except TelegramError as e:
        print(f"❌ Error mengatur commands: {e}")
        return False


async def setup_description(bot: Bot):
    """Set up bot description."""
    # Short description must be 1-120 characters (for search results)
    short_description = (
        "Asisten keuangan pribadi AI dengan persona JARVIS. "
        "Catat transaksi, lihat ringkasan keuangan, dan dapatkan insight AI."
    )

    about_text = """🤖 FinancialAssist - AI Financial Assistant Bot

Fitur:
• 💰 Pencatatan transaksi (pemasukan & pengeluaran)
• 📊 Ringkasan keuangan dan laporan
• 🤖 AI insights dengan persona JARVIS
• 🧭 Navigasi yang mudah dan intuitif

Bot ini membantu Anda mengelola keuangan pribadi dengan mudah melalui Telegram."""

    try:
        # Use retry helper to handle flood control automatically
        await handle_telegram_retry_after(bot.set_my_short_description, short_description)
        print("✅ Short description berhasil diatur!")

        # Wait between requests to avoid flood control
        await asyncio.sleep(1)

        await handle_telegram_retry_after(bot.set_my_description, about_text)
        print("✅ Full description berhasil diatur!")

        return True

    except TelegramError as e:
        print(f"❌ Error mengatur description: {e}")
        return False


async def main():
    """Main function."""
    print("🔧 Mengkonfigurasi Telegram Bot...\n")

    bot = Bot(token=settings.telegram_bot_token)

    try:
        # Setup commands
        print("1. Setting up bot commands...")
        commands_ok = await setup_commands()
        print()

        # Wait between major operations
        await asyncio.sleep(2)

        # Setup description
        print("2. Setting up bot description...")
        desc_ok = await setup_description(bot)
        print()

        if commands_ok and desc_ok:
            print("🎉 Konfigurasi Telegram bot selesai!")
            print("\nBot siap digunakan. Coba ketik /start di Telegram!")
        else:
            print("⚠️ Beberapa konfigurasi gagal. Cek error di atas.")

    finally:
        # Always close bot connection
        try:
            await bot.close()
        except Exception:  # nosec B110 - Acceptable to ignore errors when closing connection
            pass  # Ignore errors when closing


if __name__ == "__main__":
    asyncio.run(main())
