from sqlalchemy import Column, Integer, String, DateTime, Enum, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.models.base import Base
import enum

class UserTier(str, enum.Enum):
    FREE = "Free"
    PRO = "Pro"
    ELITE = "Elite"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    api_key = Column(String, unique=True, index=True, nullable=False)
    tier = Column(String, default=UserTier.FREE) # Using String for simplicity with SQLite/Postgres enum handling quirks, effectively Enum
    balance = Column(Float, default=1000.0) # $C87 balance - Start with 1000 welcome bonus
    daily_free_unlocks = Column(Integer, default=10) # Free unlocks per day for new users
    last_free_unlock_reset = Column(DateTime(timezone=True), server_default=func.now())
    watchlist = Column(JSONB, default=list) # ["BTC", "ETH", "SOL"]
    created_at = Column(DateTime(timezone=True), server_default=func.now())
