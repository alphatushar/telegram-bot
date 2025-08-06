#!/usr/bin/env python3
"""
Quick start script for the Telegram bot
"""

import os
import sys
import logging
from pathlib import Path

from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Ensure local modules are importable
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
load_dotenv()

from bot import main  # Import after sys.path and env setup

if __name__ == "__main__":
    bot_token = os.getenv("BOT_TOKEN")

    if not bot_token:
        logging.error("❌ BOT_TOKEN is missing. Please set it in your .env file.")
        sys.exit(1)

    logging.info("🤖 Starting SQL-based Telegram Bot...")
    logging.info("✅ Environment loaded. BOT_TOKEN found.")
    main()