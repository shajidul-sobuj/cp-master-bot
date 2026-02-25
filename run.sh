#!/bin/bash

# CP Master Bot - Run Script

echo "🏆 Starting CP Master Bot..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please run ./setup.sh first or create .env file manually"
    exit 1
fi

# Check if BOT_TOKEN is set
if ! grep -q "BOT_TOKEN=your_bot_token_here" .env; then
    echo "Starting bot..."
    python bot.py
else
    echo "❌ BOT_TOKEN not configured!"
    echo "Please edit .env file and add your bot token from @BotFather"
    exit 1
fi
