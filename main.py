#!/usr/bin/env python3
"""
All-in-One TempMail OTP Bot - Single file to run everything
"""

import sys
import os
import threading
import time
import signal
import subprocess
from typing import Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Global flags
services = {
    'bot': None,
    'server': None,
    'cli': None
}

def run_telegram_bot():
    """Run Telegram bot in thread"""
    try:
        from src.telegram_bot import main
        print("🤖 Starting Telegram Bot...")
        print("-" * 50)
        main()
    except Exception as e:
        print(f"❌ Bot error: {e}")

def run_autofill_server():
    """Run WebSocket server in thread"""
    try:
        from src.websocket_server import main
        print("🌐 Starting Auto-Fill Server...")
        print("-" * 50)
        main()
    except Exception as e:
        print(f"❌ Server error: {e}")

def run_cli_mode():
    """Run CLI mode"""
    try:
        from src.tempmail_otp import main
        print("📧 Starting CLI Mode...")
        print("-" * 50)
        main()
    except Exception as e:
        print(f"❌ CLI error: {e}")

def check_dependencies():
    """Check if all dependencies are installed"""
    required = ['requests', 'telegram', 'fastapi', 'uvicorn', 'aiohttp', 'websockets']
    missing = []
    
    for module in required:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        print("⚠️ Missing dependencies detected!")
        print(f"Missing: {', '.join(missing)}")
        print("\n📦 Installing dependencies...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencies installed!")
            return True
        except:
            print("❌ Failed to install dependencies")
            print("Please run manually: pip install -r requirements.txt")
            return False
    
    return True

def check_config():
    """Check if bot config exists"""
    config_paths = [
        'config/bot_config.json',
        'bot_config.json'
    ]
    
    for path in config_paths:
        if os.path.exists(path):
            print(f"✅ Config found: {path}")
            return True
    
    print("⚠️ Bot config not found!")
    print("Please create config/bot_config.json with your bot token")
    
    # Try to create from template
    if os.path.exists('config/bot_config.example.json'):
        print("\nTemplate found. Enter your bot token (or press Enter to skip):")
        token = input("Bot Token: ").strip()
        
        if token:
            import json
            config = {"telegram_bot_token": token}
            os.makedirs('config', exist_ok=True)
            
            with open('config/bot_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            
            print("✅ Config created!")
            return True
    
    return False

def show_menu():
    """Show main menu"""
    print("\n" + "=" * 60)
    print("TEMPMAIL OTP BOT - ALL-IN-ONE LAUNCHER")
    print("=" * 60)
    print("\nSelect mode to run:")
    print("\n1. 🚀 ALL SERVICES (Bot + Auto-Fill Server)")
    print("2. 🤖 Telegram Bot Only")
    print("3. 🌐 Auto-Fill Server Only")
    print("4. 📧 CLI Mode (Terminal)")
    print("5. 📊 Open Dashboard (Browser)")
    print("6. 🔧 Setup/Install Dependencies")
    print("7. ❌ Exit")
    print("\n" + "-" * 60)

def start_service(service_type, target_func):
    """Start a service in thread"""
    if services[service_type] and services[service_type].is_alive():
        print(f"⚠️ {service_type} already running")
        return
    
    services[service_type] = threading.Thread(target=target_func, daemon=True)
    services[service_type].start()
    time.sleep(2)  # Give time to start

def open_dashboard():
    """Open dashboard in browser"""
    import webbrowser
    url = "http://localhost:8000/dashboard"
    print(f"🌐 Opening dashboard: {url}")
    webbrowser.open(url)

def run_all_services():
    """Run bot and server together"""
    print("\n🚀 Starting all services...")
    print("=" * 60)
    
    # Start bot
    start_service('bot', run_telegram_bot)
    
    # Start server
    start_service('server', run_autofill_server)
    
    print("\n✅ All services started!")
    print("\nServices running:")
    print("  • Telegram Bot: Active")
    print("  • Auto-Fill Server: http://localhost:8000")
    print("  • Dashboard: http://localhost:8000/dashboard")
    print("\nPress Ctrl+C to stop all services")
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping all services...")
        sys.exit(0)

def run_bot_only():
    """Run only Telegram bot"""
    print("\n🤖 Running Telegram Bot only...")
    print("=" * 60)
    
    start_service('bot', run_telegram_bot)
    
    print("\n✅ Bot started!")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped")
        sys.exit(0)

def run_server_only():
    """Run only WebSocket server"""
    print("\n🌐 Running Auto-Fill Server only...")
    print("=" * 60)
    
    start_service('server', run_autofill_server)
    
    print("\n✅ Server started!")
    print("  • Server: http://localhost:8000")
    print("  • Dashboard: http://localhost:8000/dashboard")
    print("\nPress Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        sys.exit(0)

def setup_install():
    """Run setup/installation"""
    print("\n🔧 Running setup...")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required")
        return
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Install dependencies
    if check_dependencies():
        print("✅ All dependencies ready")
    
    # Check config
    if check_config():
        print("✅ Configuration ready")
    
    # Extension info
    print("\n📌 Chrome Extension Setup:")
    print("1. Open Chrome → chrome://extensions/")
    print("2. Enable Developer Mode")
    print("3. Load unpacked → Select 'extension/chrome' folder")
    print("4. Enter your Telegram User ID in extension")
    
    print("\n✅ Setup complete!")
    input("\nPress Enter to continue...")

def main():
    """Main function"""
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("🚀 Initializing TempMail OTP Bot...")
    print("-" * 60)
    
    # Quick dependency check
    if not check_dependencies():
        print("\n⚠️ Please install dependencies first!")
        print("Run: pip install -r requirements.txt")
        print("Or choose option 6 from menu")
        time.sleep(3)
    
    # Main loop
    while True:
        show_menu()
        
        try:
            choice = input("\nEnter choice (1-7): ").strip()
            
            if choice == "1":
                # Check config first
                if not check_config():
                    print("⚠️ Please setup bot config first (option 6)")
                    input("\nPress Enter to continue...")
                    continue
                run_all_services()
                
            elif choice == "2":
                # Check config first
                if not check_config():
                    print("⚠️ Please setup bot config first (option 6)")
                    input("\nPress Enter to continue...")
                    continue
                run_bot_only()
                
            elif choice == "3":
                run_server_only()
                
            elif choice == "4":
                run_cli_mode()
                input("\nPress Enter to continue...")
                
            elif choice == "5":
                open_dashboard()
                input("\nPress Enter to continue...")
                
            elif choice == "6":
                setup_install()
                
            elif choice == "7":
                print("\n👋 Goodbye!")
                sys.exit(0)
                
            else:
                print("❌ Invalid choice! Please try again.")
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Interrupted by user")
            print("👋 Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            input("\nPress Enter to continue...")

def graceful_shutdown(signum, frame):
    """Graceful shutdown handler"""
    print("\n\n🛑 Shutting down gracefully...")
    
    # Stop all services
    for service_name, service_thread in services.items():
        if service_thread and service_thread.is_alive():
            print(f"   Stopping {service_name}...")
    
    print("✅ Cleanup complete. Goodbye!")
    sys.exit(0)

if __name__ == "__main__":
    # Check if running on Replit
    if os.getenv('REPL_ID'):
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'deploy'))
            from keep_alive import keep_alive
            keep_alive()
            print("✅ Keep-alive server started for Replit")
        except:
            pass
    
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)
    
    # Run with arguments or interactive
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ['all', 'start']:
            if check_config():
                run_all_services()
            else:
                print("❌ Please configure bot first")
                sys.exit(1)
                
        elif arg in ['bot', 'telegram']:
            if check_config():
                run_bot_only()
            else:
                print("❌ Please configure bot first")
                sys.exit(1)
                
        elif arg in ['server', 'autofill']:
            run_server_only()
            
        elif arg in ['cli', 'terminal']:
            run_cli_mode()
            
        elif arg in ['setup', 'install']:
            setup_install()
            
        else:
            print(f"Unknown command: {arg}")
            print("\nUsage:")
            print("  python main.py          # Interactive menu")
            print("  python main.py all      # Run all services")
            print("  python main.py bot      # Run bot only")
            print("  python main.py server   # Run server only")
            print("  python main.py cli      # Run CLI mode")
            print("  python main.py setup    # Run setup")
            sys.exit(1)
    else:
        # Interactive mode
        main()
