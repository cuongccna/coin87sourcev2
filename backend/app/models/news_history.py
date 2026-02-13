from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func
from app.models.base import Base
import uuid

class NewsHistory(Base):
    """Content versioning for audit trail"""
    __tablename__ = "news_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    news_id = Column(Integer, ForeignKey("news.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    
    # Snapshots
    content_snapshot = Column(Text, nullable=True)
    ai_analysis_snapshot = Column(JSONB, default={})
    
    # Metadata
    changed_by = Column(String, nullable=False)  # 'crawler_v1', 'ai_worker', 'admin'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
