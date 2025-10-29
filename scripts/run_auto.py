#!/usr/bin/env python3
"""
Runner for Auto-Fill WebSocket Server
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from websocket_server import main

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 TEMPMAIL OTP AUTO-FILL SERVER")
    print("=" * 60)
    print("\n📌 Setup Instructions:")
    print("1. Install Chrome extension from 'extension/chrome' folder")
    print("2. Get your User ID from Telegram bot")
    print("3. Enter User ID in extension popup")
    print("4. Generate email in bot → Auto-fill OTP in browser!")
    print("\n" + "=" * 60 + "\n")
    
    main()
