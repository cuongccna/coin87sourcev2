from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Enum, JSON, Text
from sqlalchemy.sql import func
from app.models.base import Base
import enum

class SourceType(str, enum.Enum):
    rss = "rss"
    twitter = "twitter"
    api = "api"
    telegram = "telegram"

class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    source_type = Column(Enum(SourceType), nullable=False)
    config = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    trust_score = Column(Float, default=5.0)
    consecutive_failures = Column(Integer, default=0)
    last_error_log = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
