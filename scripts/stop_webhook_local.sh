#!/bin/bash

# Stop local webhook testing and cleanup

echo "🛑 Stopping local webhook testing..."

# Kill ngrok processes
echo "🌐 Stopping ngrok..."
pkill -f "ngrok http" 2>/dev/null || echo "No ngrok processes found"

# Kill bot processes
echo "🤖 Stopping bot..."
pkill -f "python -m src.shaliwood_voice_bot.main" 2>/dev/null || echo "No bot processes found"

# Clean up log files
if [ -f ngrok.log ]; then
    rm ngrok.log
    echo "🧹 Removed ngrok.log"
fi

# Restore .env backup if it exists
if [ -f .env.bak ]; then
    mv .env.bak .env
    echo "📝 Restored .env from backup"
fi

echo "✅ Cleanup completed" 