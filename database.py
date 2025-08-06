import logging
import os
from datetime import datetime
from contextlib import contextmanager
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from config import DATABASE_CONFIG

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

Base = declarative_base()

# Database setup
db_url = DATABASE_CONFIG.get('url', 'sqlite:///telegram_bot.db')

# Optional: Thread-safe for SQLite (ignore for Postgres)
extra_args = {}
if db_url.startswith("sqlite"):
    extra_args["connect_args"] = {"check_same_thread": False}

engine = create_engine(
    db_url,
    **extra_args,
    pool_pre_ping=True,          # Avoid stale DB connections
    pool_recycle=1800            # Recycle every 30 min to prevent timeout
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False)

# Define models
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(50))
    first_name = Column(String(50))
    last_name = Column(String(50))
    language_code = Column(String(10))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    message_id = Column(Integer)
    text = Column(Text)
    chat_id = Column(Integer)
    message_type = Column(String(20), default='text')
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="messages")

class ChatSession(Base):
    __tablename__ = 'chat_sessions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_data = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="sessions")


def init_db():
    """Initialize the database with all tables"""
    logging.info("Initializing database...")
    logging.info(f"DB Path: {os.path.abspath('telegram_bot.db')}")
    Base.metadata.create_all(bind=engine)
    logging.info("Database tables created successfully.")

@contextmanager
def get_db():
    """Yield a database session for use in context managers."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

# ----------------- Database Manager -----------------
class DatabaseManager:
    def __init__(self, session):
        self.session = session

    def get_or_create_user(self, telegram_user):
        user = self.session.query(User).filter_by(telegram_id=telegram_user.id).first()
        if not user:
            user = User(
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name,
                language_code=telegram_user.language_code
            )
            self.session.add(user)
            self.session.flush()
            logging.info(f"Created new user: {telegram_user.username or telegram_user.id}")
        return user

    def save_message(self, user_id, message_id, text, chat_id):
        msg = Message(
            user_id=user_id,
            message_id=message_id,
            text=text,
            chat_id=chat_id
        )
        self.session.add(msg)
        self.session.commit()

    def get_user_messages(self, user_id, limit=5):
        return self.session.query(Message).filter_by(user_id=user_id)\
            .order_by(Message.created_at.desc()).limit(limit).all()

    def get_user_stats(self, user_id):
        user = self.session.query(User).filter_by(telegram_id=user_id).first()
        if not user:
            return None
        message_count = self.session.query(Message).filter_by(user_id=user.id).count()
        return {
            "user": user,
            "message_count": message_count,
            "created_at": user.created_at
        }

    # @staticmethod
    # def update_user_activity(user_id, is_active=True):
    #     with get_session() as session:
    #         user = session.query(User).filter_by(id=user_id).first()
    #         if user:
    #             user.is_active = is_active
    #             user.updated_at = datetime.utcnow()
    #             logging.info(f"Updated activity for user {user_id}: {is_active}")
    #         return user

if __name__ == "__main__":
    init_db()