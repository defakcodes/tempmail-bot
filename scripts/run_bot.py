#!/usr/bin/env python3
"""
Direct runner for Telegram Bot
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from telegram_bot import main

if __name__ == "__main__":
    print("🤖 Starting TempMail OTP Telegram Bot...")
    print("-" * 40)
    main()
