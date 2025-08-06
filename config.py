import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is required to run the bot")

WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
PORT = int(os.getenv("PORT", "8080"))

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./telegram_bot.db")

if DATABASE_URL.startswith("postgresql"):
    DATABASE_CONFIG = {
        'url': DATABASE_URL,
        'pool_size': 20,
        'max_overflow': 30,
        'pool_pre_ping': True,
        'pool_recycle': 3600
    }
else:
    DATABASE_CONFIG = {
        'url': DATABASE_URL,
        'connect_args': {"check_same_thread": False}  # SQLite fix
    }

# Bot Metadata
BOT_NAME = "SQL Telegram Bot"
BOT_DESCRIPTION = "A feature-rich Telegram bot with SQL database storage"
BOT_VERSION = "1.0.0"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Webhook Settings
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

# Development
DEBUG = os.getenv("DEBUG", "False").lower() == "true"