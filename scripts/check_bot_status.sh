#!/bin/bash
# Script to check bot status in a readable format

echo "🤖 FinancialAssist Bot Status"
echo "=============================="
echo ""

# Find bot process
BOT_PID=$(ps aux | grep "python -m src.bot.main" | grep -v grep | grep -v bash | awk '{print $2}')

if [ -z "$BOT_PID" ]; then
    echo "❌ Bot is NOT running"
    echo ""
    echo "To start the bot, run:"
    echo "  cd /home/senarokalie/Desktop/financialassist"
    echo "  python -m src.bot.main"
    exit 1
fi

# Get process details
PROCESS_INFO=$(ps -p "$BOT_PID" -o pid,pcpu,pmem,etime,stat,cmd --no-headers 2>/dev/null)

if [ -z "$PROCESS_INFO" ]; then
    echo "❌ Bot process not found (PID: $BOT_PID)"
    exit 1
fi

# Parse process info
PID=$(echo "$PROCESS_INFO" | awk '{print $1}')
CPU=$(echo "$PROCESS_INFO" | awk '{print $2}')
MEM=$(echo "$PROCESS_INFO" | awk '{print $3}')
ETIME=$(echo "$PROCESS_INFO" | awk '{print $4}')
STAT=$(echo "$PROCESS_INFO" | awk '{print $5}')

# Get memory usage in MB
MEM_KB=$(ps -p "$BOT_PID" -o rss= 2>/dev/null | awk '{print $1}')
MEM_MB=$((MEM_KB / 1024))

# Status interpretation
case "$STAT" in
    S*) STATUS_DESC="Sleeping (waiting for events)" ;;
    R*) STATUS_DESC="Running" ;;
    D*) STATUS_DESC="Uninterruptible sleep (I/O)" ;;
    Z*) STATUS_DESC="Zombie (defunct)" ;;
    T*) STATUS_DESC="Stopped" ;;
    *) STATUS_DESC="Unknown" ;;
esac

# Display formatted output
echo "✅ Bot is RUNNING"
echo ""
echo "📊 Process Details:"
echo "   PID:        $PID"
echo "   CPU Usage:  ${CPU}%"
echo "   Memory:     ${MEM}% (${MEM_MB} MB)"
echo "   Uptime:     $ETIME"
echo "   Status:     $STAT ($STATUS_DESC)"
echo ""

# Check if bot is responsive (check recent log)
LOG_FILE="/tmp/bot_status_check.log"
if [ -f "$LOG_FILE" ]; then
    LAST_LOG=$(tail -1 "$LOG_FILE" 2>/dev/null)
    if [ -n "$LAST_LOG" ]; then
        echo "📝 Last Activity:"
        echo "   $LAST_LOG"
        echo ""
    fi
fi

echo "💡 Tips:"
echo "   • View logs: tail -f /var/log/financialassist/bot.log (production)"
echo "   • Stop bot:  pkill -f 'src.bot.main'"
echo "   • Restart:   pkill -f 'src.bot.main' && python -m src.bot.main"
