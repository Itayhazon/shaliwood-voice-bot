#!/bin/bash

# Setup script for local webhook testing
# This script sets up ngrok tunnel and configures the bot for local webhook testing

set -e

echo "🚀 Setting up local webhook testing environment..."

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok is not installed. Installing..."
    
    # Detect OS and install ngrok
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install ngrok
        else
            echo "❌ Homebrew not found. Please install ngrok manually from https://ngrok.com/"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        echo "📥 Downloading ngrok for Linux..."
        curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
        echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
        sudo apt update && sudo apt install ngrok
    else
        echo "❌ Unsupported OS. Please install ngrok manually from https://ngrok.com/"
        exit 1
    fi
fi

echo "✅ ngrok is installed"

# Check if ngrok is authenticated
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
    read -p "Press Enter after you've added your auth token, or type 'skip' to continue without auth: "
    
    if [ "$REPLY" != "skip" ]; then
        # Check again if auth was added
        if ! ngrok config check &> /dev/null; then
            echo "❌ ngrok is still not authenticated. Please run:"
            echo "   ngrok config add-authtoken YOUR_TOKEN"
            echo "   Then run this script again."
            exit 1
        fi
    fi
fi

echo "✅ ngrok is ready"

# Create .env.local file for webhook testing
echo "📝 Creating .env.local for webhook testing..."

cat > .env.local << EOF
# Local webhook testing configuration
# Copy these values to your .env file when running webhook mode

# Required environment variables
TELEGRAM_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
SPREADSHEET_ID=your_google_spreadsheet_id_here

# Webhook configuration for local testing
WEBHOOK_URL=https://your-ngrok-url.ngrok.io
WEBHOOK_PORT=8443
WEBHOOK_LISTEN=0.0.0.0
WEBHOOK_PATH=/webhook
WEBHOOK_SECRET=local_test_secret_123

# Optional environment variables
LOG_LEVEL=INFO
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json

# Voice message saving (for testing)
SAVE_VOICE_MESSAGES=false
VOICE_SAVE_DIR=voice_messages
EOF

echo "✅ Created .env.local template"
echo ""
echo "📋 Next steps:"
echo "1. Copy your actual values from .env to .env.local"
echo "2. Run: ./scripts/test_webhook_local.sh"
echo ""
echo "🎯 Or use the convenience script: ./scripts/test_webhook_local.sh" 