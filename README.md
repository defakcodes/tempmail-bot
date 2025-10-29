# TempMail OTP Receiver 📧

Automatic temporary email generator dengan OTP detection untuk registrasi dan verifikasi. Dilengkapi dengan **Telegram Bot Integration** untuk remote control! 🤖

## ✨ Features

### Core Features
- ✅ **Auto Generate Email** - Instant temporary email generation
- ✅ **Smart OTP Detection** - Auto detect 4-8 digit verification codes
- ✅ **Multiple Providers** - Mail.tm (primary) & GuerrillaMail (backup)
- ✅ **Auto Monitoring** - Real-time inbox monitoring dengan 3 detik interval
- ✅ **Pattern Recognition** - Support berbagai format OTP (code, verification, pin, etc)

### Telegram Bot Features
- 🤖 **Full Remote Control** - Generate & monitor via Telegram
- 📱 **User-Friendly Interface** - Reply keyboard buttons untuk easy access
- 🔔 **Instant Notifications** - Auto notify saat OTP diterima
- 📊 **Session Management** - Multiple users support
- 🧪 **OTP Testing** - Test extraction dengan `/testotp` command

### Browser Auto-Fill Extension 🆕
- 🌐 **Chrome Extension** - Auto-fill OTP langsung ke form browser
- ⚡ **Real-time WebSocket** - Instant OTP delivery
- 🎯 **Smart Detection** - Auto detect OTP fields
- 📊 **Dashboard** - Monitor connections and activity
- 🔐 **Secure** - Local connection only

## 📦 Installation

### Requirements
- Python 3.7+
- pip package manager

### Quick Setup
```bash
# Run automated setup
python setup.py

# Or manual install
pip install -r requirements.txt
```

### Dependencies List
- `requests` - HTTP requests untuk API calls
- `python-telegram-bot` - Telegram bot framework

## 🚀 Quick Start

### One Command to Run Everything:
```bash
# Interactive menu (RECOMMENDED)
python main.py

# Or direct commands:
python main.py all      # Run all services
python main.py bot      # Run bot only  
python main.py server   # Run server only
python main.py cli      # Run CLI mode
python main.py setup    # Run setup

# Windows users:
START.bat              # Double-click to run
```

**Features:**
- 🎯 Single file to manage everything
- 🚀 Auto-install missing dependencies
- ⚙️ Interactive configuration
- 📊 All services in one place

**Bot Setup:**
1. Create bot via [@BotFather](https://t.me/botfather)
2. Copy token ke `config/bot_config.json`
3. Start bot dan chat `/start`

## 🎮 Usage Examples

### Python Script Integration
```python
from tempmail_otp import TempMailGenerator

# Initialize generator
gen = TempMailGenerator(provider='auto')

# Generate temporary email
email = gen.generate_random_email()
print(f"Email: {email}")

# Wait for OTP (timeout 3 minutes)
otp = gen.wait_for_otp(timeout=180, check_interval=3)
if otp:
    print(f"OTP received: {otp}")

# Manual check inbox
messages = gen.check_inbox()
for msg in messages:
    print(f"From: {msg['from']}")
```

### Custom OTP Detection
```python
# Custom OTP length
otp = gen.wait_for_otp(timeout=120, otp_length=4)

# Extract from specific text
text = "Your verification code is 123456"
otp = gen.extract_otp(text, otp_length=6)
```

## 🤖 Telegram Bot Commands

### Basic Commands
| Command | Description |
|---------|-------------|
| `/start` | Initialize bot dengan welcome message |
| `/new` | Generate new temporary email |
| `/check` | Check inbox manually |
| `/status` | View active email session |
| `/stop` | Stop OTP monitoring |
| `/help` | Show help message |
| `/myid` | Tampilkan User ID Anda untuk Chrome Extension |
| `/testotp` | Test OTP extraction from text |

### Button Interface
Bot dilengkapi dengan Reply Keyboard untuk kemudahan:
- 📧 **Generate Email Baru** - One tap generate
- 📬 **Check Inbox** - Manual inbox check
- 📊 **Status** - Session information
- 🔄 **Monitor OTP** - Start monitoring
- ⏹ **Stop Monitor** - Stop monitoring
- ❓ **Help** - Show help

## 🌐 Supported Email Providers

### Mail.tm (Primary)
- **Stability**: ⭐⭐⭐⭐⭐
- **Features**: Full API support, reliable
- **Auth**: Bearer token (auto-handled)
- **Domains**: randomuser.me, tiffincrane.com, etc

### GuerrillaMail (Backup)
- **Stability**: ⭐⭐⭐⭐
- **Features**: No registration required
- **Auth**: Session-based
- **Domains**: guerrillamail.com variants

## ⚙️ Configuration

### Default Settings
```python
TIMEOUT = 180           # 3 minutes
CHECK_INTERVAL = 3      # Check every 3 seconds
OTP_LENGTH = 6         # Default 6 digits
PROVIDER = 'auto'      # Auto select best provider
```

### Bot Configuration (bot_config.json)
```json
{
    "telegram_bot_token": "YOUR_BOT_TOKEN",
    "check_interval": 3,
    "otp_timeout": 180,
    "max_sessions": 100
}
```

### Environment Variable
```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

## 📊 OTP Pattern Support

Bot dapat mendeteksi berbagai format OTP:

- ✅ `123456`
- ✅ `OTP: 123456`
- ✅ `Code: 123456`
- ✅ `Your verification code is 123456`
- ✅ `Kode verifikasi: 123456`
- ✅ `PIN: 123456`
- ✅ `One-time password: 123456`

## 🔧 Troubleshooting

### Common Issues & Solutions

**Bot tidak respond?**
- Pastikan token benar di `bot_config.json`
- Check internet connection
- Restart bot dengan `python telegram_bot.py`

**OTP tidak terdeteksi?**
- Test dengan `/testotp your otp text here`
- Check format OTP (harus 4-8 digit angka)
- Pastikan bukan welcome message

**Email expired terlalu cepat?**
- GuerrillaMail: ~1 hour lifetime
- Mail.tm: ~1 hour lifetime
- Generate new email jika expired

**Connection error?**
- Check internet connection
- Provider mungkin temporarily down
- Bot akan auto-retry dengan provider lain

## 🚀 Advanced Features

### Multi-User Support
- Each Telegram user has separate session
- Concurrent email generation
- Independent OTP monitoring

### Smart Message Filtering
- Auto skip welcome messages
- Detect dan ignore spam
- Focus on real OTP messages

### Error Recovery
- Auto retry failed API calls
- Provider switching on failure
- Session persistence

## 📝 Project Structure (Organized)
```
BOT/
├── src/                     # Core source code
│   ├── __init__.py         
│   ├── __version__.py      
│   ├── tempmail_otp.py     # Core tempmail functionality
│   ├── telegram_bot.py     # Telegram bot integration
│   └── websocket_server.py # Auto-fill WebSocket server
│
├── extension/              # Chrome extension
│   └── chrome/             
│       ├── manifest.json   
│       ├── background.js   
│       ├── content.js      
│       ├── popup.html      
│       └── popup.js        
│
├── deploy/                 # 🚀 Deployment configs (NEW)
│   ├── render.yaml         # Render.com
│   ├── railway.json        # Railway.app
│   ├── Dockerfile          # Docker
│   ├── Procfile           # Heroku/General
│   ├── Spacefile          # Deta Space
│   ├── .replit            # Replit
│   ├── keep_alive.py      # Replit keep-alive
│   ├── deploy.py          # Deploy helper
│   └── README.md          # Deploy guide
│
├── config/                 # Configuration
│   ├── bot_config.json     # Your bot config (git-ignored)
│   └── bot_config.example.json # Template
│
├── docs/                   # Documentation
│   ├── TELEGRAM_BOT_SETUP.md 
│   ├── AUTOFILL_SETUP.md  
│   ├── MANUAL_FILL.md
│   └── DEPLOYMENT.md      # Full deployment guide
│
├── scripts/                # Direct runners (optional)
│   ├── run_cli.py          
│   ├── run_bot.py          
│   └── run_autofill_server.py 
│
├── examples/               # Usage examples
│
├── main.py                # 🎯 MAIN FILE - Run everything from here
├── START.bat              # Windows quick launcher
├── setup.py               # Installation helper
├── requirements.txt       # Dependencies
├── README.md             
├── LICENSE               
├── CHANGELOG.md          
└── .gitignore           
```

## 🔒 Security Notes

- ⚠️ Email bersifat temporary - jangan untuk akun penting
- 🔐 Bot token harus dijaga kerahasiaannya
- 📝 OTP extracted locally - tidak disimpan di server
- 🗑️ Session data temporary - auto cleanup

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 📄 License

Open source for educational purposes. Use responsibly!

## 🌐 Browser Auto-Fill Extension

### Setup:
```bash
# 1. Start WebSocket server
python scripts/run_autofill_server.py

# 2. Install Chrome extension
# Open chrome://extensions/ → Developer Mode → Load unpacked → 'extension/chrome'

# 3. Connect with your Telegram User ID
```

## 🚀 Deployment

### Quick Deploy:
```bash
# Use deployment helper
python deploy/deploy.py

# Or deploy to specific platform:
# Replit: Import repo, uses deploy/.replit
# Railway: Auto-detects deploy/railway.json
# Docker: docker build -f deploy/Dockerfile .
```

All deployment configs are in `deploy/` folder.
See [deploy/README.md](deploy/README.md) for details.

### How It Works:
1. Generate email di Telegram bot
2. Use email on any website
3. Request OTP from website
4. OTP auto-fills in browser! ✨

**Full guide**: [docs/AUTOFILL_SETUP.md](docs/AUTOFILL_SETUP.md)

## 🌟 Upcoming Features

- 📊 Database integration untuk history
- 🔔 Service detection improvement
- ⏰ Email expiry alerts
- 📈 Analytics dashboard
- 🌍 Multi-language support

---

**Created with ❤️ for automation enthusiasts**

Repository: [https://github.com/abcdefak87/temporary-mail](https://github.com/abcdefak87/temporary-mail)
