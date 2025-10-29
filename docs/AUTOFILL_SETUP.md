# 🚀 Auto-Fill Browser Extension Setup Guide

## Overview
Auto-fill OTP codes directly from Telegram bot to your browser forms!

## Architecture
```
[Telegram Bot] → [WebSocket Server] → [Chrome Extension] → [Web Form]
```

## 📋 Prerequisites

1. **Run setup script:**
```bash
python setup.py
```

2. **Have your Telegram bot token ready**

## 🔧 Setup Steps

### Step 1: Start WebSocket Server

Open a new terminal:
```bash
python src/websocket_server.py
```

You should see:
```
🚀 Starting OTP Auto-Fill WebSocket Server...
📡 Server: http://localhost:8000
📊 Dashboard: http://localhost:8000/dashboard
### Step 2: Install Chrome Extension

1. **Open Chrome** and go to `chrome://extensions/`

2. **Enable Developer Mode** (toggle in top-right)

3. **Click "Load unpacked"**

4. **Select folder**: `extension/chrome/`

5. **Extension not showing?**
   • Click 'Load unpacked'
   • Select folder: extension/chrome/
   • Note: Icons are optional, extension works without them

6. **Extension installed!** You'll see the icon in toolbar

### Step 3: Connect Extension to Bot
1. **Get your Telegram User ID:**
   - Gunakan command `/myid` di Telegram bot
   - User ID akan ditampilkan dan bisa di-copy
   - Atau lihat di welcome message saat `/start`
   - Format: angka seperti `123456789`

2. **Click extension icon** in Chrome toolbar

3. **Enter your User ID** and click **Connect**

4. **Status should show**: ✅ Connected

## 📱 How to Use

### Automatic Flow:
1. **Generate email** in Telegram bot
2. **Use email** on any website  
3. **Request OTP** from website
4. **Bot receives OTP** → Auto-fills in browser! ✨

### Manual Flow:
1. When OTP received, **extension shows notification**
2. Click **Auto-Fill** button in extension popup
3. Or click **Copy** to copy OTP

## 🎯 Supported Websites

Extension auto-detects OTP fields on:
- ✅ Shopee
- ✅ Tokopedia  
- ✅ Gojek
- ✅ Grab
- ✅ Banking sites
- ✅ Social media
- ✅ Most websites with OTP fields

## 🔍 How It Works

### OTP Field Detection:
Extension looks for inputs with:
- Names: `otp`, `code`, `verification`, `pin`
- Placeholders: `Enter OTP`, `Verification Code`
- Type: 6-digit number fields
- Split fields: 6 separate boxes

### Auto-Fill Logic:
1. Detects OTP input fields
2. Fills the value
3. Triggers input events
4. Highlights submit button
5. Shows success notification

## 📊 Dashboard

Open dashboard: http://localhost:8000/dashboard

Features:
- Live connection status
- OTP delivery stats
- Activity log
- Real-time monitoring

## ⚙️ Configuration

### Extension Settings:
Edit `extension/chrome/background.js`:
```javascript
// WebSocket server URL
const WEBSOCKET_URL = 'ws://localhost:8000/ws/';

// Auto-submit after fill (disabled by default)
const AUTO_SUBMIT = false;

// Notification duration
const NOTIFICATION_DURATION = 5000;
```

### Server Settings:
Edit `src/websocket_server.py`:
```python
# Server port
PORT = 8000

# CORS origins (for production, specify exact domains)
ALLOWED_ORIGINS = ["*"]
```

## 🔧 Troubleshooting

### Extension Not Connecting?
1. Check WebSocket server is running
2. Verify User ID is correct
3. Check Chrome console for errors (F12 → Console)

### OTP Not Auto-Filling?
1. Refresh the webpage
2. Check if field is detected (console will show logs)
3. Try manual fill from extension popup

### Server Connection Error?
```bash
# Check if port 8000 is available
netstat -an | grep 8000

# Kill process using port
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -i:8000
kill -9 <PID>
```

## 🔒 Security Notes

1. **Local Only**: Server runs on localhost only
2. **User ID**: Acts as simple authentication
3. **No Storage**: OTPs are not stored
4. **HTTPS**: For production, use HTTPS/WSS

## 🎨 Customization

### Add New OTP Pattern:
Edit `extension/chrome/content.js`:
```javascript
const OTP_SELECTORS = [
  // Add your selector
  'input[name="your-otp-field"]',
];
```

### Custom Service Detection:
Edit `src/telegram_bot.py`:
```python
services = {
  'your-service': ['your-domain.com'],
}
```

## 📈 Advanced Features

### Multiple Users:
- Each user has unique ID
- Supports unlimited concurrent users
- Independent sessions

### Browser Support:
Current: Chrome/Edge
Planned: Firefox, Safari

### Mobile Support:
- Kiwi Browser (Android) supports extensions
- Safari (iOS) - planned

## 🚀 Production Deployment

For production use:

1. **Use HTTPS/WSS:**
```python
# Use SSL certificates
uvicorn.run(app, ssl_keyfile="key.pem", ssl_certfile="cert.pem")
```

2. **Deploy server to cloud:**
- Deploy WebSocket server to VPS/Cloud
- Update extension to use your server URL

3. **Publish extension:**
- Package extension
- Submit to Chrome Web Store

## 📝 API Reference

### WebSocket Messages:

**OTP Message:**
```json
{
  "type": "otp",
  "otp": "123456",
  "email": "temp@mail.com",
  "sender": "Shopee",
  "timestamp": 1234567890
}
```

**Status Message:**
```json
{
  "type": "status",
  "connected": true,
  "email": "current@mail.com"
}
```

### REST Endpoints:

**Send OTP:**
```
POST /api/otp
Body: {
  "user_id": "123",
  "otp": "123456",
  "email": "temp@mail.com",
  "sender": "Service Name"
}
```

**Register Email:**
```
POST /api/email
Body: {
  "user_id": "123",
  "email": "new@mail.com"
}
```

## 🎉 Tips & Tricks

1. **Test Mode**: Use `/testotp 123456` in bot to test
2. **Debug Mode**: Open Chrome DevTools to see logs
3. **Force Fill**: Right-click field → Extension → Fill OTP
4. **Quick Connect**: Save User ID for auto-connect

## 📞 Support

Issues? Check:
1. Console logs (F12)
2. Server logs
3. Extension popup status
4. Network tab for WebSocket

---

**Enjoy seamless OTP auto-fill!** 🎊
