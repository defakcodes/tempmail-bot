# 📦 Deployment Configurations

This folder contains all deployment configurations for various hosting platforms.

## 📁 Files

### Platform-Specific Configs:
- **`render.yaml`** - Render.com configuration
- **`railway.json`** - Railway.app configuration  
- **`Dockerfile`** - Docker container configuration
- **`.dockerignore`** - Docker ignore file
- **`Procfile`** - Heroku/general deployment
- **`Spacefile`** - Deta Space configuration
- **`.replit`** - Replit configuration
- **`keep_alive.py`** - Keep-alive server for Replit

### Helper Scripts:
- **`deploy.py`** - Interactive deployment helper

## 🚀 Quick Deploy

### Replit (FREE):
1. Import repo to Replit
2. File `.replit` will auto-configure
3. Add bot token in Secrets
4. Run!

### Railway ($5 credit):
1. Connect GitHub
2. Railway auto-detects `railway.json`
3. Add environment variables
4. Deploy!

### Docker (Any VPS):
```bash
docker build -t tempmail-bot .
docker run -d -e TELEGRAM_BOT_TOKEN=your_token tempmail-bot
```

### Deploy Helper:
```bash
python deploy/deploy.py
```

## 📝 Environment Variables

All platforms need:
- `TELEGRAM_BOT_TOKEN` - Your bot token from @BotFather

## 📚 Full Guide

See [docs/DEPLOYMENT.md](../docs/DEPLOYMENT.md) for detailed instructions.
