#!/bin/bash
# Bot control script with readable status

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

case "$1" in
    status|check)
        "$SCRIPT_DIR/check_bot_status.sh"
        ;;
    start)
        echo "🚀 Starting FinancialAssist Bot..."
        cd "$PROJECT_DIR" || exit 1

        # Check if already running
        if ps aux | grep "python -m src.bot.main" | grep -v grep | grep -v bash > /dev/null; then
            echo "⚠️  Bot is already running!"
            "$SCRIPT_DIR/check_bot_status.sh"
            exit 1
        fi

        # Start bot in background
        nohup python -m src.bot.main > /tmp/bot.log 2>&1 &
        sleep 2

        if ps aux | grep "python -m src.bot.main" | grep -v grep | grep -v bash > /dev/null; then
            echo "✅ Bot started successfully!"
            "$SCRIPT_DIR/check_bot_status.sh"
        else
            echo "❌ Failed to start bot. Check /tmp/bot.log for errors."
            exit 1
        fi
        ;;
    stop)
        echo "🛑 Stopping FinancialAssist Bot..."
        BOT_PID=$(ps aux | grep "python -m src.bot.main" | grep -v grep | grep -v bash | awk '{print $2}')

        if [ -z "$BOT_PID" ]; then
            echo "⚠️  Bot is not running."
            exit 0
        fi

        kill "$BOT_PID" 2>/dev/null
        sleep 2

        if ps -p "$BOT_PID" > /dev/null 2>&1; then
            echo "⚠️  Bot did not stop gracefully. Force killing..."
            kill -9 "$BOT_PID" 2>/dev/null
        fi

        echo "✅ Bot stopped."
        ;;
    restart)
        echo "🔄 Restarting FinancialAssist Bot..."
        "$0" stop
        sleep 1
        "$0" start
        ;;
    logs)
        echo "📝 Bot Logs (last 20 lines):"
        echo "=============================="
        if [ -f "/var/log/financialassist/bot.log" ]; then
            tail -20 /var/log/financialassist/bot.log
        elif [ -f "/tmp/bot.log" ]; then
            tail -20 /tmp/bot.log
        else
            echo "No log file found."
        fi
        ;;
    *)
        echo "🤖 FinancialAssist Bot Control"
        echo "=============================="
        echo ""
        echo "Usage: $0 {status|start|stop|restart|logs}"
        echo ""
        echo "Commands:"
        echo "  status   - Show bot status (readable format)"
        echo "  start    - Start the bot"
        echo "  stop     - Stop the bot"
        echo "  restart  - Restart the bot"
        echo "  logs     - Show recent logs"
        echo ""
        exit 1
        ;;
esac
