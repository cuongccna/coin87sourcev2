from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from app.models.base import Base
import enum

class TransactionType(str, enum.Enum):
    EARN_VOTE = "EARN_VOTE"
    EARN_REFERRAL = "EARN_REFERRAL"
    SPEND_UNLOCK = "SPEND_UNLOCK"
    SPEND_BOOST = "SPEND_BOOST"
    SPEND_BADGE = "SPEND_BADGE"

class Transaction(Base):
    """$C87 Token transaction ledger"""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)  # Positive for earn, negative for spend
    balance_after = Column(Float, nullable=False)
    
    # Metadata
    related_news_id = Column(Integer, ForeignKey("news.id"), nullable=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
