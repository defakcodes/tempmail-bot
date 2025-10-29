# 📱 Telegram Bot Setup Guide

## Langkah 1: Buat Bot di Telegram

1. **Buka Telegram** dan cari `@BotFather`
2. **Start chat** dengan BotFather
3. **Kirim command** `/newbot`
4. **Beri nama bot** (contoh: `TempMail OTP Bot`)
5. **Beri username** (harus diakhiri `bot`, contoh: `tempmail_otp_bot`)
6. **Simpan token** yang diberikan (format: `1234567890:ABCdefGHIjklmnoPQRSTuvwxyz123456789`)

## Langkah 2: Install Dependencies

```bash
pip install python-telegram-bot
```

Atau install semua:
```bash
pip install -r requirements.txt
```

## Langkah 3: Konfigurasi Bot

### Option A: Menggunakan Config File
1. Copy template config:
```bash
cp bot_config.example.json bot_config.json
```

2. Edit `bot_config.json`:
```json
{
    "telegram_bot_token": "YOUR_BOT_TOKEN_HERE"
}
```

### Option B: Menggunakan Environment Variable
```bash
# Windows (Command Prompt)
set TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE

# Windows (PowerShell)
$env:TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN_HERE"

# Linux/Mac
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
```

## Langkah 4: Run Bot

```bash
python telegram_bot.py
```

Bot akan start dan siap menerima command!

## Langkah 5: Test Bot

1. **Buka Telegram** dan cari username bot Anda
2. **Start chat** dengan bot
3. **Kirim** `/start` untuk memulai
4. **Kirim** `/new` untuk generate email

## 📋 Command List

| Command | Fungsi |
|---------|--------|
| `/start` | Start bot dan lihat welcome message |
| `/new` | Generate temporary email baru |
| `/check` | Check inbox secara manual |
| `/status` | Lihat status email aktif |
| `/otp` | Start monitoring untuk OTP |
| `/stop` | Stop OTP monitoring |
| `/help` | Tampilkan bantuan |

## 🎯 Features Bot

- ✅ **Auto Generate Email** - Buat email temporary instant
- ✅ **Real-time OTP Detection** - Auto detect berbagai format OTP
- ✅ **Push Notification** - Terima notif saat OTP diterima
- ✅ **Inline Keyboard** - Button untuk quick actions
- ✅ **Multi-user Support** - Banyak user bisa pakai bersamaan
- ✅ **Session Management** - Track email per user

## ⚙️ Advanced Configuration

Edit `telegram_bot.py` untuk customize:

```python
class BotConfig:
    TOKEN = ""  # Your bot token
    CHECK_INTERVAL = 3  # Check inbox setiap 3 detik
    OTP_TIMEOUT = 180  # Timeout 3 menit
    MAX_SESSIONS = 100  # Max concurrent users
```

## 🔧 Troubleshooting

### Bot tidak respond?
- Pastikan token benar
- Check internet connection
- Pastikan bot sudah di-start di Telegram

### Error "Unauthorized"?
- Token salah atau invalid
- Generate token baru dari BotFather

### OTP tidak terdeteksi?
- Check format OTP di email
- Bot support format: 4-8 digit angka
- Bisa customize pattern di `tempmail_otp.py`

## 🔒 Security Tips

1. **Jangan share bot token** ke publik
2. **Gunakan .gitignore** untuk exclude `bot_config.json`
3. **Set bot private** jika hanya untuk personal use
4. **Regular check** bot activity via BotFather

## 📱 Mobile Usage

Bot bisa diakses dari:
- Telegram Mobile (Android/iOS)
- Telegram Desktop
- Telegram Web
- Telegram X

## 🎨 Customization

### Custom Welcome Message
Edit function `start()` di `telegram_bot.py`

### Custom OTP Pattern
Edit function `extract_otp()` di `tempmail_otp.py`

### Add More Providers
Extend class `TempMailGenerator` dengan provider baru

## 📊 Bot Analytics

Track bot usage dengan:
- User count: Check `user_sessions` dict
- Success rate: Log OTP detection
- Popular times: Add timestamp logging

## 🚀 Deploy to Cloud (Optional)

Deploy bot ke cloud untuk 24/7 uptime:

### Heroku
1. Create `Procfile`:
```
worker: python telegram_bot.py
```

2. Deploy ke Heroku

### VPS
1. Use `screen` atau `tmux`
2. Run: `python telegram_bot.py`
3. Detach session

### Docker
1. Create `Dockerfile`
2. Build & run container

## 📝 Notes

- Bot gratis untuk personal use
- Telegram API limit: 30 messages/second
- Simpan backup token
- Bot bisa handle multiple users

## 🆘 Need Help?

- Check `/help` command di bot
- Read Telegram Bot API docs
- Check python-telegram-bot documentation

---

**Happy Botting! 🤖**
