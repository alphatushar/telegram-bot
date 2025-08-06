import logging
from functools import wraps
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.orm import Session
from contextlib import contextmanager
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

from database import init_db, DatabaseManager, get_db
from config import BOT_TOKEN, WEBHOOK_URL, PORT

# -------------------- Logging --------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# -------------------- Initialize DB --------------------
init_db()

# -------------------- DB Decorator --------------------
def with_db(func):
    """Decorator to provide DB session to handlers via context.db"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        with get_db() as session:
            context.db = DatabaseManager(session)
            return await func(update, context, *args, **kwargs)
    return wrapper

# -------------------- Handlers --------------------
@with_db
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message and store user."""
    user = update.effective_user
    context.db.get_or_create_user(user)

    keyboard = [
        [InlineKeyboardButton("📊 My Stats", callback_data='stats')],
        [InlineKeyboardButton("💬 Recent Messages", callback_data='messages')],
        [InlineKeyboardButton("❓ Help", callback_data='help')]
    ]

    await update.message.reply_html(
        f"👋 Hello {user.mention_html()}!\n\n"
        "Welcome to the SQL-based Telegram Bot!\n"
        "I'm logging all your messages to the database.\n\n"
        "Use the buttons below to explore features:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@with_db
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*Available Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/stats - Show your statistics\n"
        "/messages - Show your recent messages\n\n"
        "*Features:*\n"
        "✅ Stores all messages in SQL database\n"
        "✅ Tracks user activity\n"
        "✅ Provides usage statistics\n"
        "✅ Shows message history",
        parse_mode='Markdown'
    )

@with_db
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user statistics."""
    user_id = update.effective_user.id
    stats = context.db.get_user_stats(user_id)

    if stats:
        user = stats['user']
        await update.message.reply_text(
            f"*Your Statistics:* 📊\n\n"
            f"👤 User ID: `{user.telegram_id}`\n"
            f"📝 Username: @{user.username or 'N/A'}\n"
            f"📧 Messages Sent: {stats['message_count']}\n"
            f"📅 Account Created: {stats['created_at'].strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"✅ Status: {'Active' if user.is_active else 'Inactive'}",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("No statistics found. Send a message first!")

@with_db
async def messages_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show recent messages."""
    user_id = update.effective_user.id
    messages = context.db.get_user_messages(user_id, limit=5)

    if messages:
        text = "*Your Recent Messages:*\n\n"
        for msg in reversed(messages):
            time = msg.created_at.strftime("%H:%M:%S")
            preview = msg.text[:50] + "..." if len(msg.text) > 50 else msg.text
            text += f"🕐 {time} - {preview}\n"
    else:
        text = "No messages found. Start chatting!"

    await update.message.reply_text(text, parse_mode='Markdown')

@with_db
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle normal messages."""
    user = update.effective_user
    message = update.effective_message
    text = message.text.strip().lower()

    # Save to DB
    db_user = context.db.get_or_create_user(user)
    context.db.save_message(
        user_id=db_user.id,
        message_id=message.message_id,
        text=message.text,
        chat_id=message.chat_id
    )

    # Simple responses
    if text in ['hello', 'hi', 'hey']:
        await message.reply_text(f"👋 Hello {user.first_name or 'there'}! Your message is saved. 📊")
    else:
        await message.reply_text(
            "✅ Message saved!\n\n"
            "💡 Send /stats to see your statistics\n"
            "💡 Send /messages to see your recent messages"
        )

@with_db
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()

    # Route based on callback data
    if query.data == 'stats':
        await stats_command(update, context)
    elif query.data == 'messages':
        await messages_command(update, context)
    elif query.data == 'help':
        await help_command(update, context)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

# -------------------- Main --------------------
def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not found. Please set it in your .env file.")
        return

    application = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("messages", messages_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_error_handler(error_handler)

    # Start bot: Prefer polling for simplicity
    if WEBHOOK_URL:
        logger.info("Starting bot in webhook mode...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        #application.run_webhook(listen="0.0.0.0", port=PORT, webhook_url=WEBHOOK_URL)
    else:
        logger.info("Starting bot in polling mode...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()