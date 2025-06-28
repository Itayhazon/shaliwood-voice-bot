#!/bin/bash

# Run cron processing for Shaliwood Voice Bot
# This script processes recent Telegram messages in batch

set -e

echo "🕐 Shaliwood Voice Bot - Cron Processing"
echo "========================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create one with your configuration."
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

# Run cron processing using the root cron_processor.py
echo "🚀 Starting cron processing..."
echo ""

poetry run python cron_processor.py

echo ""
echo "✅ Cron processing completed!" 