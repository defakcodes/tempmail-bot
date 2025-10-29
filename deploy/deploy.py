#!/usr/bin/env python3
"""
Deployment helper for TempMail OTP Bot
"""

import os
import sys
import json
import subprocess

def show_menu():
    """Show deployment menu"""
    print("\n" + "=" * 60)
    print("📦 DEPLOYMENT HELPER")
    print("=" * 60)
    print("\n1. 🌟 Deploy to Render (Free)")
    print("2. 🚂 Deploy to Railway")
    print("3. 🎈 Deploy to Fly.io")
    print("4. 🐳 Deploy with Docker")
    print("5. 📝 Create Environment File")
    print("6. 📚 View Deployment Guide")
    print("7. ❌ Exit")
    print("\n" + "-" * 60)

def create_env_file():
    """Create environment configuration"""
    print("\n📝 Creating environment configuration...")
    
    token = input("Enter your Telegram Bot Token: ").strip()
    if not token:
        print("❌ Token required!")
        return
    
    # Create .env file in root
    with open('../.env', 'w') as f:
        f.write(f"TELEGRAM_BOT_TOKEN={token}\n")
        f.write("PORT=8000\n")
    
    print("✅ Created .env file")
    
    # Update config
    os.makedirs('../config', exist_ok=True)
    config = {"telegram_bot_token": token}
    
    with open('../config/bot_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Updated config/bot_config.json")

def deploy_render():
    """Deploy to Render"""
    print("\n🌟 Deploying to Render.com...")
    print("\nSteps:")
    print("1. Push your code to GitHub")
    print("2. Go to https://render.com")
    print("3. Connect your GitHub repo")
    print("4. Select 'Background Worker' for bot")
    print("5. Use these settings:")
    print("   Build: pip install -r requirements.txt")
    print("   Start: python main.py bot")
    print("\n✅ render.yaml already configured!")
    print("\nPress Enter to open Render.com...")
    input()
    
    import webbrowser
    webbrowser.open("https://render.com")

def deploy_railway():
    """Deploy to Railway"""
    print("\n🚂 Deploying to Railway...")
    
    # Check if railway CLI installed
    try:
        subprocess.run(["railway", "--version"], capture_output=True, check=True)
        print("✅ Railway CLI found")
        
        print("\nDeploying...")
        subprocess.run(["railway", "up"])
        
    except:
        print("❌ Railway CLI not installed")
        print("\nInstall with: npm i -g @railway/cli")
        print("Then run: railway login")
        print("\n✅ railway.json already configured!")

def deploy_flyio():
    """Deploy to Fly.io"""
    print("\n🎈 Deploying to Fly.io...")
    
    # Check if fly CLI installed
    try:
        subprocess.run(["fly", "version"], capture_output=True, check=True)
        print("✅ Fly CLI found")
        
        print("\nInitializing app...")
        app_name = input("Enter app name (leave blank for auto): ").strip()
        
        if app_name:
            subprocess.run(["fly", "launch", "--name", app_name])
        else:
            subprocess.run(["fly", "launch"])
            
    except:
        print("❌ Fly CLI not installed")
        print("\nInstall from: https://fly.io/docs/hands-on/install-flyctl/")

def deploy_docker():
    """Deploy with Docker"""
    print("\n🐳 Deploying with Docker...")
    
    # Check if docker installed
    try:
        subprocess.run(["docker", "--version"], capture_output=True, check=True)
        print("✅ Docker found")
        
        print("\nBuilding image...")
        subprocess.run(["docker", "build", "-t", "tempmail-bot", "."])
        
        print("\nRunning container...")
        token = input("Enter Bot Token (or press Enter to use .env): ").strip()
        
        if token:
            subprocess.run([
                "docker", "run", "-d",
                "-e", f"TELEGRAM_BOT_TOKEN={token}",
                "-p", "8000:8000",
                "--name", "tempmail-bot",
                "tempmail-bot"
            ])
        else:
            subprocess.run([
                "docker", "run", "-d",
                "--env-file", ".env",
                "-p", "8000:8000",
                "--name", "tempmail-bot",
                "tempmail-bot"
            ])
        
        print("✅ Container started!")
        print("\nCommands:")
        print("  docker logs -f tempmail-bot    # View logs")
        print("  docker stop tempmail-bot       # Stop")
        print("  docker rm tempmail-bot         # Remove")
        
    except:
        print("❌ Docker not installed")
        print("\nInstall from: https://docs.docker.com/get-docker/")

def view_guide():
    """Open deployment guide"""
    guide_path = "docs/DEPLOYMENT.md"
    
    if os.path.exists(guide_path):
        print("\n📚 Opening deployment guide...")
        
        if sys.platform == "win32":
            os.startfile(guide_path)
        elif sys.platform == "darwin":
            subprocess.run(["open", guide_path])
        else:
            subprocess.run(["xdg-open", guide_path])
    else:
        print("❌ Guide not found!")

def main():
    """Main function"""
    while True:
        show_menu()
        
        choice = input("\nSelect option (1-7): ").strip()
        
        if choice == "1":
            deploy_render()
        elif choice == "2":
            deploy_railway()
        elif choice == "3":
            deploy_flyio()
        elif choice == "4":
            deploy_docker()
        elif choice == "5":
            create_env_file()
        elif choice == "6":
            view_guide()
        elif choice == "7":
            print("\n👋 Goodbye!")
            sys.exit(0)
        else:
            print("❌ Invalid choice!")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    print("🚀 TempMail Bot Deployment Helper")
    print("-" * 40)
    main()
