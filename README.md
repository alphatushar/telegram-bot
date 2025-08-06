# SQL-Based Telegram Chat Bot

A feature-rich Telegram bot that stores all user interactions in a SQL database with support for both SQLite and PostgreSQL.

## Features

- ✅ **User Management**: Automatically tracks and stores user information
- ✅ **Message Storage**: Saves all user messages with timestamps
- ✅ **Statistics**: Provides user activity statistics
- ✅ **Message History**: View recent messages
- ✅ **Database Support**: SQLite (development) and PostgreSQL (production)
- ✅ **Interactive Buttons**: Clean UI with inline keyboards
- ✅ **Error Handling**: Comprehensive logging and error management

## Installation

1. **Clone or download the bot files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your bot token and database settings
   ```

4. **Get your bot token**:
   - Message @BotFather on Telegram
   - Create a new bot with `/newbot`
   - Copy the token to your `.env` file

## Usage

### Development (SQLite)
```bash
# Set up environment
echo "BOT_TOKEN=your_bot_token_here" > .env
echo "DATABASE_URL=sqlite:///telegram_bot.db" >> .env

# Run the bot
python bot.py
```

### Production (PostgreSQL)
```bash
# Set up PostgreSQL database
createdb telegram_bot

# Set up environment
echo "BOT_TOKEN=your_bot_token_here" > .env
echo "DATABASE_URL=postgresql://username:password@localhost:5432/telegram_bot" >> .env

# Run the bot
python bot.py
```

## Commands

- `/start` - Start the bot and see welcome message
- `/help` - Show available commands
- `/stats` - Display your statistics
- `/messages` - Show your recent messages

## Database Schema

### Users Table
- `id`: Primary key
- `telegram_id`: Unique Telegram user ID
- `username`: Telegram username
- `first_name`: User's first name
- `last_name`: User's last name
- `language_code`: User's language preference
- `is_active`: User activity status
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp

### Messages Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `message_id`: Telegram message ID
- `text`: Message content
- `chat_id`: Telegram chat ID
- `message_type`: Type of message (text, photo, etc.)
- `created_at`: Message timestamp

### Chat Sessions Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `session_data`: JSON session data
- `created_at`: Session creation timestamp
- `updated_at`: Last update timestamp

## API Usage

The bot provides database operations through the `DatabaseManager` class:

```python
from database import get_db, DatabaseManager

with next(get_db()) as session:
    db = DatabaseManager(session)
    
    # Get or create user
    user = db.get_or_create_user(telegram_user)
    
    # Save message
    message = db.save_message(user_id, message_id, text, chat_id)
    
    # Get user stats
    stats = db.get_user_stats(user_id)
    
    # Get user messages
    messages = db.get_user_messages(user_id, limit=10)
```

## Deployment Options

### Local Development
```bash
python bot.py
```

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

### Heroku
1. Add `Procfile`:
   ```
   web: python bot.py
   ```
2. Set environment variables in Heroku dashboard
3. Deploy with git push

## Webhook Setup (Optional)

For production deployment with webhooks:

1. Set `WEBHOOK_URL` in `.env`
2. Set `PORT` in `.env`
3. The bot will automatically use webhook mode

## Troubleshooting

### Common Issues

1. **"BOT_TOKEN not found"**
   - Ensure `.env` file exists and contains valid `BOT_TOKEN`

2. **Database connection errors**
   - Check `DATABASE_URL` format
   - Ensure PostgreSQL is running (if using PostgreSQL)

3. **Permission errors**
   - Ensure bot has permission to send messages
   - Check if bot is added to group/channel (if applicable)

### Logs
Check the console output for detailed error messages. The bot includes comprehensive logging for debugging.

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - feel free to use this bot for any purpose.
