#!/bin/bash

# Start local webhook testing
# This script starts the bot in webhook mode with automatic ngrok setup

set -e

echo "🎯 Shaliwood Voice Bot - Starting Local Webhook Testing"
echo "========================================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Creating from template..."
    if [ -f .env.local ]; then
        cp .env.local .env
        echo "✅ Created .env from .env.local template"
        echo "📝 Please update the values in .env with your actual credentials"
        exit 1
    else
        echo "❌ Neither .env nor .env.local found. Run setup first:"
        echo "   ./scripts/setup_webhook_local.sh"
        exit 1
    fi
fi

# Check if ngrok is installed and authenticated
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok not found. Running setup..."
    ./scripts/setup_webhook_local.sh
    exit 1
fi

if ! ngrok config check &> /dev/null; then
    echo ""
    echo "🔑 ngrok requires authentication (free account)"
    echo "================================================"
    echo "1. Go to: https://dashboard.ngrok.com/signup"
    echo "2. Sign up for a FREE account"
    echo "3. After signing up, go to: https://dashboard.ngrok.com/get-started/your-authtoken"
    echo "4. Copy your auth token"
    echo ""
    echo "Then run this command (replace YOUR_TOKEN with your actual token):"
    echo "   ngrok config add-authtoken YOUR_TOKEN"
    echo ""
    echo "After adding your token, run this script again."
    exit 1
fi

# Check if poetry is available
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry not found. Please install poetry first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Install dependencies
echo "📦 Installing dependencies..."
poetry install

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🧹 Cleaning up..."
    if [ ! -z "$NGROK_PID" ]; then
        kill $NGROK_PID 2>/dev/null || true
        echo "✅ Stopped ngrok"
    fi
    if [ ! -z "$BOT_PID" ]; then
        kill $BOT_PID 2>/dev/null || true
        echo "✅ Stopped bot"
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo ""
echo "🚀 Starting local webhook testing..."
echo ""

# Start ngrok in background
echo "🌐 Starting ngrok tunnel..."
ngrok http 8443 > ngrok.log 2>&1 &
NGROK_PID=$!

# Wait for ngrok to start and get the URL
echo "⏳ Waiting for ngrok to start..."
sleep 5

# Try multiple patterns to extract the HTTPS URL from ngrok output
NGROK_URL=""

# Method 1: Try the original pattern
NGROK_URL=$(grep -o 'https://[a-z0-9]*\.ngrok\.io' ngrok.log | head -1)

# Method 2: Try newer ngrok format with app.ngrok.io
if [ -z "$NGROK_URL" ]; then
    NGROK_URL=$(grep -o 'https://[a-z0-9]*\.app\.ngrok\.io' ngrok.log | head -1)
fi

# Method 3: Try any https URL pattern
if [ -z "$NGROK_URL" ]; then
    NGROK_URL=$(grep -o 'https://[a-z0-9-]*\.ngrok\.io' ngrok.log | head -1)
fi

# Method 4: Look for the forwarding line
if [ -z "$NGROK_URL" ]; then
    NGROK_URL=$(grep "Forwarding" ngrok.log | grep -o 'https://[^[:space:]]*' | head -1)
fi

# Method 5: Check if ngrok is running and get URL from ngrok API
if [ -z "$NGROK_URL" ]; then
    echo "🔍 Trying to get URL from ngrok API..."
    sleep 2
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*"' | cut -d'"' -f4 | head -1)
fi

if [ -z "$NGROK_URL" ]; then
    echo "❌ Failed to get ngrok URL. Check ngrok.log for details."
    echo "📋 ngrok.log contents:"
    cat ngrok.log
    echo ""
    echo "📋 Common issues:"
    echo "   - ngrok not authenticated (run: ngrok config add-authtoken YOUR_TOKEN)"
    echo "   - port 8443 already in use"
    echo "   - network connectivity issues"
    echo "   - ngrok output format changed"
    cleanup
    exit 1
fi

echo "✅ ngrok tunnel established: $NGROK_URL"

# Update .env with the ngrok URL
echo "📝 Updating .env with ngrok URL..."

# Check if WEBHOOK_URL exists in .env, if not add it
if ! grep -q "WEBHOOK_URL" .env; then
    echo "" >> .env
    echo "# Webhook configuration for local testing" >> .env
    echo "WEBHOOK_URL=$NGROK_URL" >> .env
    echo "WEBHOOK_PORT=8443" >> .env
    echo "WEBHOOK_LISTEN=0.0.0.0" >> .env
    echo "WEBHOOK_PATH=/webhook" >> .env
    
    # Generate a secure webhook secret
    WEBHOOK_SECRET=$(openssl rand -hex 32)
    echo "WEBHOOK_SECRET=$WEBHOOK_SECRET" >> .env
    echo "✅ Added webhook configuration to .env"
    echo "🔐 Generated secure webhook secret: $WEBHOOK_SECRET"
else
    # Update existing WEBHOOK_URL
    sed -i.bak "s|WEBHOOK_URL=.*|WEBHOOK_URL=$NGROK_URL|" .env
    echo "✅ Updated WEBHOOK_URL to: $NGROK_URL"
    
    # Check if WEBHOOK_SECRET exists and is secure
    if ! grep -q "WEBHOOK_SECRET" .env; then
        WEBHOOK_SECRET=$(openssl rand -hex 32)
        echo "WEBHOOK_SECRET=$WEBHOOK_SECRET" >> .env
        echo "🔐 Added secure webhook secret: $WEBHOOK_SECRET"
    else
        CURRENT_SECRET=$(grep "WEBHOOK_SECRET=" .env | cut -d'=' -f2)
        if [ "$CURRENT_SECRET" = "local_test_secret_123" ] || [ ${#CURRENT_SECRET} -lt 32 ]; then
            WEBHOOK_SECRET=$(openssl rand -hex 32)
            sed -i.bak "s|WEBHOOK_SECRET=.*|WEBHOOK_SECRET=$WEBHOOK_SECRET|" .env
            echo "🔐 Updated to secure webhook secret: $WEBHOOK_SECRET"
        fi
    fi
fi

# Start the bot in webhook mode
echo "🤖 Starting bot in webhook mode..."
poetry run python -m src.shaliwood_voice_bot.main &
BOT_PID=$!

echo ""
echo "🎉 Local webhook testing is now running!"
echo "================================================"
echo "🌐 Webhook URL: $NGROK_URL"
echo "🤖 Bot is running in webhook mode"
echo "📱 You can now send messages to your Telegram bot"
echo ""
echo "📋 To stop testing, run: ./scripts/stop_webhook_local.sh"
echo "📋 Or press Ctrl+C to stop immediately"
echo "📋 To view ngrok logs: tail -f ngrok.log"
echo "📋 To view bot logs: Check the bot output above"
echo ""

# Wait for user to stop
wait 