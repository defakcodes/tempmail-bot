#!/bin/bash
# Deploy TempMail Bot to Linux Server (24/7)

echo "🚀 TempMail Bot - Linux Deployment Script"
echo "=========================================="

# Get current directory
INSTALL_DIR=$(pwd)
echo "📁 Install directory: $INSTALL_DIR"

# Check if running as root (not recommended)
if [ "$EUID" -eq 0 ]; then 
    echo "⚠️  Warning: Running as root. Consider using a non-root user."
fi

# 1. Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# 2. Setup environment variables
echo ""
echo "⚙️  Setting up environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env file"
    echo "⚠️  Please edit .env and add your TELEGRAM_BOT_TOKEN"
    read -p "Press Enter after editing .env..."
else
    echo "✅ .env already exists"
fi

# 3. Create log directory
echo ""
echo "📝 Creating log directory..."
sudo mkdir -p /var/log/tempmail-bot
sudo chown $USER:$USER /var/log/tempmail-bot
echo "✅ Log directory created"

# 4. Setup systemd service
echo ""
echo "🔧 Setting up systemd service..."

# Update service file with correct paths
SERVICE_FILE="tempmail-bot.service"
TEMP_SERVICE="/tmp/tempmail-bot.service"

sed "s|YOUR_USERNAME|$USER|g" $SERVICE_FILE > $TEMP_SERVICE
sed -i "s|/path/to/temporary-mail-main|$INSTALL_DIR|g" $TEMP_SERVICE

# Install service
sudo cp $TEMP_SERVICE /etc/systemd/system/tempmail-bot.service
sudo systemctl daemon-reload

echo "✅ Systemd service installed"

# 5. Enable and start service
echo ""
echo "🎯 Starting service..."
sudo systemctl enable tempmail-bot.service
sudo systemctl start tempmail-bot.service

# 6. Check status
echo ""
echo "📊 Service Status:"
sudo systemctl status tempmail-bot.service --no-pager

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "📋 Useful Commands:"
echo "   Start:   sudo systemctl start tempmail-bot"
echo "   Stop:    sudo systemctl stop tempmail-bot"
echo "   Restart: sudo systemctl restart tempmail-bot"
echo "   Status:  sudo systemctl status tempmail-bot"
echo "   Logs:    sudo journalctl -u tempmail-bot -f"
echo "   or:      tail -f /var/log/tempmail-bot/output.log"
echo ""
echo "🌐 Dashboard: http://YOUR_SERVER_IP:8000/dashboard"
echo ""
