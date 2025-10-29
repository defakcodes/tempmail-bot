#!/usr/bin/env python3
"""
Setup and installation script for TempMail OTP Bot
"""

import os
import sys
import json
import subprocess
import platform
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from __version__ import __version__, __description__

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_dependencies():
    """Install required packages"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All dependencies installed")
        return True
    except:
        print("❌ Failed to install dependencies")
        return False

def setup_config():
    """Setup configuration"""
    print("\n⚙️ Setting up configuration...")
    
    config_file = "config/bot_config.json"
    example_file = "config/bot_config.example.json"
    
    if os.path.exists(config_file):
        print("✅ Configuration already exists")
        return True
    
    if os.path.exists(example_file):
        print("📝 Please configure your bot:")
        print(f"   1. Copy {example_file} to {config_file}")
        print("   2. Add your Telegram bot token")
        return False
    
    return True

def setup_extension():
    """Setup Chrome extension"""
    print("\n🌐 Chrome Extension Setup:")
    print("-" * 40)
    print("1. Open Chrome and go to: chrome://extensions/")
    print("2. Enable 'Developer mode' (top right)")
    print("3. Click 'Load unpacked'")
    print(f"4. Select folder: {os.path.abspath('extension/chrome')}")
    print("5. Extension will be installed!")
    print("\nNote: Extension works without icon files")
    return True

def print_usage():
    """Print usage instructions"""
    print("\n" + "=" * 60)
    print(f"✅ SETUP COMPLETE! (v{__version__})")
    print("=" * 60)
    
    print("\n📚 How to use:\n")
    
    print("1️⃣ Start Telegram Bot:")
    print("   python scripts/run_bot.py")
    print("   OR: run.bat (Windows) / ./run.sh (Linux/Mac)\n")
    
    print("2️⃣ Start Auto-Fill Server (optional):")
    print("   python scripts/run_autofill_server.py\n")
    
    print("3️⃣ Use the bot:")
    print("   - Open Telegram and find your bot")
    print("   - Send /start to begin")
    print("   - Generate temporary email")
    print("   - Receive OTP automatically!\n")
    
    print("4️⃣ Auto-Fill in Browser:")
    print("   - Install Chrome extension (see above)")
    print("   - Enter your Telegram User ID")
    print("   - OTP will auto-fill in forms!\n")
    
    print("=" * 60)

def main():
    """Main setup function"""
    print("=" * 60)
    print("🚀 TEMPMAIL OTP SETUP")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install dependencies
    if not install_dependencies():
        return 1
    
    # Setup config
    if not setup_config():
        print("\n⚠️ Please configure bot_config.json first")
        return 1
    
    # Setup extension info
    setup_extension()
    
    # Print usage
    print_usage()
    
    # Ask to start
    print("\n❓ Start services now? (y/n): ", end="")
    choice = input().strip().lower()
    
    if choice == 'y':
        print("\nStarting bot...")
        if platform.system() == "Windows":
            os.system("start python scripts/run_bot.py")
            print("\n❓ Start auto-fill server too? (y/n): ", end="")
            if input().strip().lower() == 'y':
                os.system("start python scripts/run_autofill_server.py")
        else:
            print("Run these commands in separate terminals:")
            print("  python scripts/run_bot.py")
            print("  python scripts/run_autofill_server.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
