from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint, Enum
from sqlalchemy.sql import func
from app.models.base import Base
import enum

class VoteOrigin(str, enum.Enum):
    HUMAN = "HUMAN"
    SYSTEM_BOT = "SYSTEM_BOT"

class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    news_id = Column(Integer, ForeignKey("news.id"), nullable=False)
    vote_type = Column(String, nullable=False) # 'trust' | 'fake'
    origin = Column(String, default="HUMAN", index=True)  # VARCHAR in DB (was Enum before migration)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('user_id', 'news_id', name='unique_user_vote'),
    )
