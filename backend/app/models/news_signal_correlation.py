"""
Model: News Signal Correlation
Lưu enhanced trust score từ trading signals
"""

from sqlalchemy import Column, Integer, Float, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.models.base import Base


class NewsSignalCorrelation(Base):
    """Bảng liên kết news với trading signals để tính enhanced trust score"""
    
    __tablename__ = "news_signal_correlation"
    
    id = Column(Integer, primary_key=True, index=True)
    news_id = Column(Integer, ForeignKey("news.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Foreign keys đến signals tables
    smart_money_signal_id = Column(Integer, ForeignKey("smart_money_signals.id", ondelete="SET NULL"))
    sentiment_report_id = Column(Integer, ForeignKey("sentiment_reports.id", ondelete="SET NULL"))
    onchain_intelligence_id = Column(Integer, ForeignKey("onchain_intelligence.id", ondelete="SET NULL"))
    
    # Cached trust scores
    enhanced_trust_score = Column(Float, nullable=False)
    base_trust_score = Column(Float, nullable=False)
    smart_money_bonus = Column(Float, default=0.0)
    sentiment_bonus = Column(Float, default=0.0)
    onchain_bonus = Column(Float, default=0.0)
    
    # Metadata
    time_diff_seconds = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    news = relationship("News", back_populates="signal_correlation")
    smart_money_signal = relationship("SmartMoneySignal")
    sentiment_report = relationship("SentimentReport")
    onchain_intelligence = relationship("OnChainIntelligence")
