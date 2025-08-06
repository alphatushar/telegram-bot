#!/usr/bin/env python3
"""
Setup script for the Telegram bot
"""

import os
import subprocess
import sys
import traceback


def check_python_version():
    """Check if Python 3.7+ is installed"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")


def install_dependencies():
    """Install required packages"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)


def create_env_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            print("📝 Creating .env file...")
            with open('.env.example', 'r') as f:
                content = f.read()
            with open('.env', 'w') as f:
                f.write(content)
            print("✅ .env file created from .env.example")
            print("⚠️  Please edit .env with your actual bot token")
        else:
            print("⚠️  .env.example not found. Please create a .env file manually.")
    else:
        print("✅ .env file already exists")


def init_database():
    """Initialize the database"""
    try:
        choice = input("🗄️  Initialize database now? (y/N): ").strip().lower()
        if choice != "y":
            print("ℹ️  Skipping database initialization.")
            return

        print("🗄️  Initializing database...")
        from database import init_db
        init_db()
        print("✅ Database initialized successfully")
    except Exception:
        print("❌ Failed to initialize database:")
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main setup function"""
    print("🔧 Setting up SQL-based Telegram Bot...")
    print("=" * 50)

    check_python_version()
    install_dependencies()
    create_env_file()
    init_database()

    print("=" * 50)
    print("🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Edit .env with your bot token from @BotFather")
    print("2. Run: python run.py")
    print("3. Check README.md for usage and troubleshooting")


if __name__ == "__main__":
    main()