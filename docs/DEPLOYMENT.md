# 🚀 Deployment Guide - Hosting TempMail OTP Bot

## 📊 Platform Comparison

| Platform | Free Tier | Best For | Limitations |
|----------|-----------|----------|-------------|
| **Render** ⭐ | 750 hrs/month | Full bot + server | Sleeps after 15 min |
| **Railway** | $5 credit | Quick deploy | Limited free usage |
| **Fly.io** | 3 VMs free | 24/7 uptime | Complex setup |
| **Replit** | Unlimited* | Testing | Needs keepalive |
| **VPS** | Varies | Full control | Not free |

---

## 🌟 Option 1: Render.com (RECOMMENDED)

### Steps:
1. **Create Account**: https://render.com

2. **Connect GitHub**:
   - Fork/push repo to GitHub
   - Connect GitHub to Render

3. **Create New Service**:
   - Click "New +" → "Background Worker"
   - Select your repo
   - Use `render.yaml` config

4. **Set Environment Variables**:
   ```
   TELEGRAM_BOT_TOKEN = your_bot_token_here
   ```

5. **Deploy**:
   - Click "Create Background Worker"
   - Wait for deployment

### Render Commands:
```yaml
# Already configured in render.yaml
Build: pip install -r requirements.txt
Start: python main.py bot
```

---

## 🚂 Option 2: Railway.app

### Steps:
1. **Create Account**: https://railway.app

2. **New Project**:
   ```bash
   # Install Railway CLI
   npm i -g @railway/cli
   
   # Login
   railway login
   
   # Deploy
   railway up
   ```

3. **Set Variables**:
   ```bash
   railway variables set TELEGRAM_BOT_TOKEN=your_token_here
   ```

4. **Deploy from GitHub**:
   - Connect GitHub repo
   - Railway auto-detects `railway.json`
   - Auto deploys

---

## 🎈 Option 3: Fly.io

### Steps:
1. **Install Fly CLI**:
   ```bash
   # Windows
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   
   # Linux/Mac
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**:
   ```bash
   fly auth login
   ```

3. **Create App**:
   ```bash
   fly launch --name tempmail-bot
   ```

4. **Create fly.toml**:
   ```toml
   app = "tempmail-bot"
   
   [processes]
   bot = "python main.py bot"
   server = "python main.py server"
   
   [[services]]
   processes = ["server"]
   http_checks = []
   internal_port = 8000
   protocol = "tcp"
   
   [[services.ports]]
   port = 80
   handlers = ["http"]
   
   [[services.ports]]
   port = 443
   handlers = ["tls", "http"]
   ```

5. **Set Secrets**:
   ```bash
   fly secrets set TELEGRAM_BOT_TOKEN=your_token_here
   ```

6. **Deploy**:
   ```bash
   fly deploy
   ```

---

## 🔧 Option 4: VPS (DigitalOcean/Vultr/Linode)

### Setup Script:
```bash
#!/bin/bash

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3 python3-pip git -y

# Clone repo
git clone https://github.com/yourusername/tempmail-bot.git
cd tempmail-bot

# Install dependencies
pip3 install -r requirements.txt

# Create config
cat > config/bot_config.json << EOF
{
  "telegram_bot_token": "YOUR_BOT_TOKEN"
}
EOF

# Install as systemd service
sudo cat > /etc/systemd/system/tempmail-bot.service << EOF
[Unit]
Description=TempMail OTP Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/tempmail-bot
ExecStart=/usr/bin/python3 /home/$USER/tempmail-bot/main.py all
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl daemon-reload
sudo systemctl enable tempmail-bot
sudo systemctl start tempmail-bot
```

---

## 🐳 Option 5: Docker Deployment

### Docker Compose:
```yaml
version: '3.8'

services:
  bot:
    build: .
    command: python main.py bot
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    restart: unless-stopped
    
  server:
    build: .
    command: python main.py server
    ports:
      - "8000:8000"
    restart: unless-stopped
```

### Deploy Commands:
```bash
# Build
docker-compose build

# Run
docker-compose up -d

# Check logs
docker-compose logs -f
```

---

## 🌐 Option 6: Replit

### Steps:
1. **Import from GitHub**: https://replit.com/new

2. **Create `.replit` file**:
   ```toml
   run = "python main.py all"
   language = "python3"
   
   [packager]
   ignoredPackages = ["discord.py"]
   ```

3. **Create keep_alive.py**:
   ```python
   from flask import Flask
   from threading import Thread
   
   app = Flask('')
   
   @app.route('/')
   def home():
       return "Bot is alive!"
   
   def run():
       app.run(host='0.0.0.0', port=8080)
   
   def keep_alive():
       t = Thread(target=run)
       t.start()
   ```

4. **Use UptimeRobot**: https://uptimerobot.com
   - Monitor your Replit URL
   - Ping every 5 minutes

---

## 🔐 Environment Variables Setup

### Required Variables:
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
PORT=8000  # For web server
```

### Platform-Specific:

**Render**:
- Dashboard → Environment → Add Variable

**Railway**:
- Variables tab → Add Variable

**Fly.io**:
```bash
fly secrets set TELEGRAM_BOT_TOKEN=xxx
```

**Heroku**:
```bash
heroku config:set TELEGRAM_BOT_TOKEN=xxx
```

---

## 📝 Deployment Checklist

- [ ] Fork/push code to GitHub
- [ ] Create account on hosting platform
- [ ] Set environment variables
- [ ] Configure build commands
- [ ] Deploy and test
- [ ] Setup monitoring (optional)
- [ ] Configure custom domain (optional)

---

## 🆓 Free Hosting Recommendations

### For 24/7 Bot:
1. **Fly.io** - 3 free VMs
2. **Railway** - $5 credit (lasts ~1 week)
3. **Render** - 750 hours/month

### For Testing:
1. **Replit** - With UptimeRobot
2. **Gitpod** - 50 hours/month
3. **GitHub Codespaces** - 60 hours/month

### For Production:
1. **VPS** - $5/month (DigitalOcean, Vultr)
2. **AWS EC2** - t2.micro free tier
3. **Google Cloud** - f1-micro free tier

---

## 🚨 Important Notes

1. **Free tiers have limitations** - May sleep or have usage limits
2. **Use environment variables** - Never commit tokens
3. **Monitor your bot** - Use services like UptimeRobot
4. **Backup config** - Keep local copies
5. **Scale when needed** - Upgrade when user base grows

---

## 💡 Quick Deploy Commands

### Render:
```bash
# No CLI needed, use web dashboard
```

### Railway:
```bash
railway up
```

### Fly.io:
```bash
fly deploy
```

### Heroku:
```bash
git push heroku main
```

### Docker:
```bash
docker-compose up -d
```

---

## 📞 Support

Issues with deployment? Check:
1. Environment variables set correctly
2. Dependencies installed
3. Port configurations
4. Platform logs for errors
