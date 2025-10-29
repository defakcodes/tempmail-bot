#!/usr/bin/env python3
"""
Telegram Bot Integration for TempMail OTP Receiver
Bot untuk generate temporary email dan menerima OTP via Telegram
"""

import logging
import asyncio
import os
from typing import Dict, Optional
from datetime import datetime
import json
import aiohttp

# Telegram bot libraries
from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Import tempmail generator
from tempmail_otp import TempMailGenerator

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Store user sessions
user_sessions: Dict[int, Dict] = {}

# Constants
SESSION_EXPIRY = 3600  # 1 hour in seconds
CLEANUP_INTERVAL = 300  # 5 minutes
AUTOFILL_SERVER_URL = os.getenv('AUTOFILL_SERVER_URL', 'http://localhost:8000')

# Bot configuration
class BotConfig:
    """Bot configuration"""
    TOKEN = ""  # Your bot token here
    CHECK_INTERVAL = 3  # seconds
    OTP_TIMEOUT = 180  # 3 minutes
    MAX_SESSIONS = 100  # Max concurrent sessions


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send message when /start command issued"""
    user = update.effective_user
    
    # Create main menu keyboard
    keyboard = [
        [KeyboardButton("📧 Generate Email Baru"), KeyboardButton("📬 Check Inbox")],
        [KeyboardButton("📊 Status"), KeyboardButton("🔄 Monitor OTP")],
        [KeyboardButton("⏹ Stop Monitor"), KeyboardButton("❓ Help")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_message = f"""
🤖 *TempMail OTP Bot*

Halo {user.first_name}! 👋

Saya adalah bot untuk generate temporary email dan menerima kode OTP secara otomatis.

*Features:*
✅ Auto generate temporary email
✅ Real-time OTP monitoring  
✅ Multiple provider support
✅ Auto notification saat OTP diterima

*Quick Start:*
Tap "📧 Generate Email Baru" untuk mulai!

*Your User ID:* `{user.id}`
Gunakan /myid untuk melihat info lengkap
    """
    
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def new_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate new temporary email"""
    user_id = update.effective_user.id
    
    # Send loading message
    loading_msg = await update.message.reply_text("⏳ Generating new email...")
    
    try:
        # Initialize generator
        generator = TempMailGenerator(provider='auto')
        email = generator.generate_random_email()
        
        # Store session
        user_sessions[user_id] = {
            'generator': generator,
            'email': email,
            'created_at': datetime.now(),
            'otp_monitoring': False,
            'messages_checked': set()
        }
        
        # Edit loading message without button
        await loading_msg.edit_text(
            f"✅ *Email Berhasil Dibuat!*\n\n"
            f"📧 Email:\n`{email}`\n\n"
            f"📌 *Instruksi:*\n"
            f"1️⃣ Tap email di atas untuk copy\n"
            f"2️⃣ Gunakan untuk registrasi\n"
            f"3️⃣ OTP akan auto terdeteksi\n\n"
            f"⏱️ _Auto monitoring aktif..._",
            parse_mode='Markdown'
        )
        
        # Auto start OTP monitoring (only if not already running)
        if not user_sessions[user_id].get('otp_monitoring', False):
            context.application.create_task(
                monitor_otp_background(update, context, user_id)
            )
        else:
            logger.warning(f"OTP monitoring already active for user {user_id}")
        
        # Send to auto-fill server
        await send_email_to_autofill(str(user_id), email)
        
    except Exception as e:
        await loading_msg.edit_text(f"❌ Error: {str(e)}")


async def check_inbox(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check inbox manually"""
    user_id = update.effective_user.id
    
    if user_id not in user_sessions:
        await update.message.reply_text(
            "❌ Tidak ada email aktif.\nGunakan /new untuk generate email baru."
        )
        return
    
    session = user_sessions[user_id]
    generator = session['generator']
    
    loading_msg = await update.message.reply_text("📬 Checking inbox...")
    
    try:
        messages = generator.check_inbox()
        
        if messages:
            response = f"📨 *Inbox ({len(messages)} messages):*\n\n"
            
            for i, msg in enumerate(messages[:5], 1):  # Show max 5 messages
                # Skip welcome messages in display
                if "welcome" in msg.get('subject', '').lower():
                    continue
                    
                response += f"*{i}. Message:*\n"
                response += f"📤 From: {msg.get('from', 'Unknown')}\n"
                response += f"📝 Subject: {msg.get('subject', 'No subject')}\n"
                response += f"🕐 Time: {msg.get('date', 'Unknown')}\n"
                
                # Try to extract OTP from this message
                full_msg = generator.get_message_content(msg.get('id'))
                if full_msg:
                    text_to_check = (
                        full_msg.get('subject', '') + ' ' +
                        full_msg.get('body', '') + ' ' +
                        full_msg.get('htmlBody', '')
                    )
                    otp = generator.extract_otp(text_to_check)
                    if otp:
                        response += f"🔑 *OTP Found: `{otp}`*\n"
                    else:
                        preview = full_msg.get('body', '')[:100] if full_msg.get('body') else ''
                        response += f"📄 Preview: _{preview}_...\n"
                
                response += "─" * 30 + "\n"
            
            await loading_msg.edit_text(response, parse_mode='Markdown')
        else:
            await loading_msg.edit_text("📭 Inbox kosong")
            
    except Exception as e:
        await loading_msg.edit_text(f"❌ Error checking inbox: {str(e)}")


async def monitor_otp_background(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_id: int
) -> None:
    """Background task to monitor OTP"""
    
    if user_id not in user_sessions:
        return
    
    session = user_sessions[user_id]
    generator = session['generator']
    session['otp_monitoring'] = True
    
    # Send notification
    await context.bot.send_message(
        chat_id=user_id,
        text=f"🔄 *OTP Monitoring Started*\n\n"
        f"Email: `{session['email']}`\n"
        f"Timeout: 3 minutes\n\n"
        f"Saya akan notify jika OTP diterima.",
        parse_mode='Markdown'
    )
    
    start_time = asyncio.get_event_loop().time()
    timeout = BotConfig.OTP_TIMEOUT
    
    while session.get('otp_monitoring', False):
        # Check timeout
        if asyncio.get_event_loop().time() - start_time > timeout:
            await context.bot.send_message(
                chat_id=user_id,
                text="⏱️ *Timeout!*\nTidak ada OTP dalam 3 menit.\n\nGunakan /otp untuk monitor lagi.",
                parse_mode='Markdown'
            )
            break
        
        try:
            # Check for new messages
            messages = generator.check_inbox()
            
            for msg in messages:
                msg_id = msg.get('id')
                
                # Skip if already checked
                if msg_id in session['messages_checked']:
                    continue
                
                session['messages_checked'].add(msg_id)
                
                # Get full message
                full_msg = generator.get_message_content(msg_id)
                
                if full_msg:
                    # Extract OTP
                    text_to_check = (
                        full_msg.get('subject', '') + ' ' +
                        full_msg.get('body', '') + ' ' +
                        full_msg.get('htmlBody', '')
                    )
                    
                    otp = generator.extract_otp(text_to_check)
                    
                    if otp:
                        # OTP found!
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=f"🎉 *OTP BERHASIL DITERIMA!*\n\n"
                            f"📧 Email:\n`{session['email']}`\n\n"
                            f"🔑 *OTP Code:*\n`{otp}`\n\n"
                            f"📨 From: {msg.get('from', 'Unknown')}\n\n"
                            f"_Tap OTP di atas untuk copy_",
                            parse_mode='Markdown'
                        )
                        
                        # Send to auto-fill server if enabled
                        await send_otp_to_autofill(
                            user_id=str(user_id),
                            otp=otp,
                            email=session['email'],
                            sender=msg.get('from', 'Unknown')
                        )
                        
                        session['otp_monitoring'] = False
                        return
                    else:
                        # Skip welcome messages
                        if "welcome" in msg.get('subject', '').lower() or "guerrilla" in msg.get('from', '').lower():
                            continue
                            
                        # New message but no OTP - show preview
                        message_preview = full_msg.get('body', '')[:200] if full_msg.get('body') else 'No content'
                        
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=f"📨 *Pesan baru* (no OTP detected)\n\n"
                            f"From: {msg.get('from', 'Unknown')}\n"
                            f"Subject: {msg.get('subject', 'No subject')}\n\n"
                            f"Preview:\n_{message_preview}_\n\n"
                            f"⚠️ _OTP tidak terdeteksi. Cek format OTP._",
                            parse_mode='Markdown'
                        )
        
        except Exception as e:
            logger.error(f"Error monitoring OTP: {e}")
        
        # Wait before next check
        await asyncio.sleep(BotConfig.CHECK_INTERVAL)
    
    session['otp_monitoring'] = False


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show current email status"""
    user_id = update.effective_user.id
    
    if user_id not in user_sessions:
        await update.message.reply_text(
            "❌ Tidak ada email aktif.\nGunakan /new untuk generate email baru."
        )
        return
    
    session = user_sessions[user_id]
    created_time = session['created_at']
    elapsed = (datetime.now() - created_time).seconds
    
    status_text = f"""
📊 *Status Email*

📧 Email: `{session['email']}`
⏱️ Created: {elapsed} seconds ago
🔄 OTP Monitor: {'Active ✅' if session.get('otp_monitoring', False) else 'Inactive ❌'}
📨 Messages checked: {len(session.get('messages_checked', set()))}

_Email akan expired dalam {180 - elapsed} seconds_
    """
    
    keyboard = [
        [InlineKeyboardButton("📬 Check Inbox", callback_data='check_inbox')],
        [InlineKeyboardButton("🔄 Start OTP Monitor", callback_data='start_otp')],
        [InlineKeyboardButton("🆕 Generate New", callback_data='new_email')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        status_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def stop_monitoring(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stop OTP monitoring"""
    user_id = update.effective_user.id
    
    if user_id in user_sessions:
        user_sessions[user_id]['otp_monitoring'] = False
        await update.message.reply_text("⏹️ OTP monitoring stopped.")
    else:
        await update.message.reply_text("❌ Tidak ada monitoring aktif.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages from reply keyboard"""
    text = update.message.text
    
    if text == "📧 Generate Email Baru":
        await new_email(update, context)
    elif text == "📬 Check Inbox":
        await check_inbox(update, context)
    elif text == "📊 Status":
        await status(update, context)
    elif text == "🔄 Monitor OTP":
        user_id = update.effective_user.id
        if user_id in user_sessions:
            if not user_sessions[user_id].get('otp_monitoring', False):
                context.application.create_task(
                    monitor_otp_background(update, context, user_id)
                )
                await update.message.reply_text("🔄 OTP monitoring started!")
            else:
                await update.message.reply_text("⚠️ OTP monitoring sudah aktif!")
        else:
            await update.message.reply_text("❌ Generate email dulu dengan '📧 Generate Email Baru'")
    elif text == "⏹ Stop Monitor":
        await stop_monitoring(update, context)
    elif text == "❓ Help":
        await help_command(update, context)
    else:
        await update.message.reply_text(
            "⚠️ Gunakan button menu di bawah atau ketik /help untuk bantuan"
        )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks"""
    query = update.callback_query
    user_id = query.from_user.id
    
    if query.data == 'check_inbox':
        await query.answer()
        # Manual check inbox
        if user_id not in user_sessions:
            await query.message.reply_text(
                "❌ Session expired. Gunakan /new untuk generate email baru."
            )
            return
        
        session = user_sessions[user_id]
        generator = session['generator']
        
        try:
            messages = generator.check_inbox()
            
            if messages:
                response = f"📨 *Inbox ({len(messages)} messages):*\n\n"
                for msg in messages[:5]:
                    response += f"From: {msg.get('from', 'Unknown')}\n"
                    response += f"Subject: {msg.get('subject', 'No subject')}\n\n"
                
                await query.message.reply_text(response, parse_mode='Markdown')
            else:
                await query.message.reply_text("📭 Inbox kosong")
        
        except Exception as e:
            await query.message.reply_text(f"❌ Error: {str(e)}")
    
    elif query.data == 'start_otp':
        await query.answer()
        # Start OTP monitoring
        if user_id not in user_sessions:
            await query.message.reply_text(
                "❌ Session expired. Gunakan /new untuk generate email baru."
            )
            return
        
        if user_sessions[user_id].get('otp_monitoring', False):
            await query.message.reply_text("⚠️ OTP monitoring sudah aktif!")
        else:
            context.application.create_task(
                monitor_otp_background(query, context, user_id)
            )
    
    


async def test_otp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Test OTP extraction from text"""
    # Get text after command
    text = ' '.join(context.args) if context.args else ''
    
    if not text:
        await update.message.reply_text(
            "📝 *Test OTP Extraction*\n\n"
            "Usage: `/testotp [text with otp]`\n\n"
            "Example:\n"
            "`/testotp Your verification code is 123456`",
            parse_mode='Markdown'
        )
        return
    
    # Try to extract OTP
    from tempmail_otp import TempMailGenerator
    gen = TempMailGenerator()
    
    # Try different OTP lengths
    found_otps = []
    for length in [4, 5, 6, 7, 8]:
        otp = gen.extract_otp(text, otp_length=length)
        if otp and otp not in found_otps:
            found_otps.append(otp)
    
    if found_otps:
        response = "✅ *OTP Detected!*\n\n"
        for otp in found_otps:
            response += f"🔑 `{otp}` ({len(otp)} digits)\n"
    else:
        response = "❌ *No OTP detected*\n\n"
        response += f"Text checked:\n_{text}_\n\n"
        response += "Tips: OTP should be 4-8 consecutive digits"
    
    await update.message.reply_text(response, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help message"""
    help_text = """
📖 *Help - TempMail OTP Bot*

*Commands:*
• /new - Generate temporary email baru
• /check - Check inbox secara manual
• /status - Lihat status email aktif
• /stop - Stop OTP monitoring
• /testotp - Test OTP extraction
• /myid - Tampilkan User ID Anda
• /help - Tampilkan bantuan ini

*How to Use:*
1. Gunakan /new untuk generate email
2. Copy email untuk registrasi
3. Bot akan auto monitor inbox
4. Terima notifikasi saat OTP diterima

*Features:*
• Auto generate temporary email
• Real-time OTP detection
• Support Mail.tm & GuerrillaMail
• Auto notification via Telegram

*Browser Extension Setup:*
Silakan baca docs/AUTOFILL_SETUP.md
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def show_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menampilkan Telegram User ID pengguna"""
    user = update.effective_user
    user_id = user.id
    
    # Buat pesan dengan info lengkap
    message = f"""🔑 *Informasi User ID Anda*

📱 *User ID:* `{user_id}`
👤 *Nama:* {user.first_name} {user.last_name if user.last_name else ''}
🏷️ *Username:* @{user.username if user.username else 'Tidak ada'}

📌 *Gunakan User ID ini untuk:*
• Chrome Extension auto-fill
• Integrasi dengan aplikasi lain
• WebSocket connection

💡 *Tips:*
Tap User ID di atas untuk copy ke clipboard!"""
    
    await update.message.reply_text(
        message,
        parse_mode='Markdown'
    )


async def send_otp_to_autofill(user_id: str, otp: str, email: str, sender: str):
    """Send OTP to auto-fill server"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{AUTOFILL_SERVER_URL}/api/otp",
                json={
                    "user_id": user_id,
                    "otp": otp,
                    "email": email,
                    "sender": sender,
                    "domain": detect_service_domain(sender)
                },
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    # Mask OTP in logs for security
                    logger.info(f"✅ OTP sent to auto-fill for user {user_id}")
    except Exception as e:
        logger.debug(f"Auto-fill server not available: {e}")


async def send_email_to_autofill(user_id: str, email: str):
    """Send new email to auto-fill server"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{AUTOFILL_SERVER_URL}/api/email",
                json={
                    "user_id": user_id,
                    "email": email
                },
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    logger.info(f"✅ Email sent to auto-fill: {email}")
    except Exception as e:
        logger.debug(f"Auto-fill server not available: {e}")


def detect_service_domain(sender: str) -> str:
    """Detect service from sender email"""
    sender_lower = sender.lower()
    
    services = {
        'shopee': ['shopee.com', 'shopee.co.id'],
        'tokopedia': ['tokopedia.com'],
        'gojek': ['gojek.com', 'go-jek.com'],
        'grab': ['grab.com'],
        'dana': ['dana.id'],
        'ovo': ['ovo.id'],
        'google': ['google.com', 'googlemail.com'],
        'facebook': ['facebook.com', 'facebookmail.com'],
        'twitter': ['twitter.com'],
        'instagram': ['instagram.com']
    }
    
    for service, domains in services.items():
        for domain in domains:
            if domain in sender_lower:
                return service
    
    return ''


async def cleanup_expired_sessions():
    """Background task to cleanup expired sessions"""
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL)
        
        current_time = datetime.now()
        expired_users = []
        
        for user_id, session in user_sessions.items():
            created_at = session.get('created_at')
            if created_at:
                elapsed = (current_time - created_at).total_seconds()
                if elapsed > SESSION_EXPIRY:
                    expired_users.append(user_id)
        
        for user_id in expired_users:
            logger.info(f"Cleaning up expired session for user {user_id}")
            user_sessions.pop(user_id, None)
        
        if expired_users:
            logger.info(f"Cleaned up {len(expired_users)} expired sessions")


def main():
    """Start the bot"""
    # Get bot token from environment or config file
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    if not bot_token:
        # Try to load from config file
        config_paths = [
            'config/bot_config.json',
            'bot_config.json',
            '../config/bot_config.json'
        ]
        
        for config_path in config_paths:
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    bot_token = config.get('telegram_bot_token', '')
                    if bot_token:
                        break
            except:
                continue
    
    if not bot_token:
        print("❌ Bot token tidak ditemukan!")
        print("\nCara setting bot token:")
        print("1. Set environment variable: TELEGRAM_BOT_TOKEN")
        print("2. Atau buat file config/bot_config.json dengan format:")
        print('   {"telegram_bot_token": "YOUR_BOT_TOKEN"}')
        print("\n📝 Copy template: cp config/bot_config.example.json config/bot_config.json")
        return
    
    # Create application
    application = Application.builder().token(bot_token).build()
    
    # Start cleanup task
    application.create_task(cleanup_expired_sessions())
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("new", new_email))
    application.add_handler(CommandHandler("check", check_inbox))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("stop", stop_monitoring))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("myid", show_user_id))
    application.add_handler(CommandHandler("testotp", test_otp))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start bot
    print("🤖 TempMail OTP Bot Started!")
    print("Press Ctrl+C to stop")
    
    # Run bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
