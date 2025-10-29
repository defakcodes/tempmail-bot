#!/bin/bash
# Quick start script - Run bot in background using screen

echo "🚀 Starting TempMail Bot in background..."

# Check if screen is installed
if ! command -v screen &> /dev/null; then
    echo "❌ 'screen' not installed. Installing..."
    sudo apt-get install -y screen
fi

# Check if already running
if screen -list | grep -q "tempmail-bot"; then
    echo "⚠️  Bot already running!"
    echo "To view: screen -r tempmail-bot"
    echo "To stop: screen -S tempmail-bot -X quit"
    exit 1
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check bot token
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN not set!"
    echo "Please edit .env file or run:"
    echo "export TELEGRAM_BOT_TOKEN='your_token_here'"
    exit 1
fi

# Create logs directory
mkdir -p logs

# Start in screen
screen -dmS tempmail-bot bash -c "python3 main.py all 2>&1 | tee logs/bot.log"

sleep 2

# Check if started
if screen -list | grep -q "tempmail-bot"; then
    echo "✅ Bot started successfully!"
    echo ""
    echo "📋 Commands:"
    echo "   View logs:   tail -f logs/bot.log"
    echo "   Attach:      screen -r tempmail-bot"
    echo "   Detach:      Ctrl+A, then D"
    echo "   Stop:        screen -S tempmail-bot -X quit"
    echo ""
    echo "🌐 Dashboard: http://$(hostname -I | awk '{print $1}'):8000/dashboard"
else
    echo "❌ Failed to start bot"
    exit 1
fi
