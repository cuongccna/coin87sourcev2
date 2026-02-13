from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import enum

class CategoryType(enum.Enum):
    MARKET_MOVE = "market_move"
    PROJECT_UPDATE = "project_update"
    PARTNERSHIP = "partnership"
    SECURITY = "security"
    OPINION = "opinion"

class VerificationStatus(enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    FLAGGED = "flagged"
    DEBUNKED = "debunked"

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    title = Column(String, nullable=False)
    url = Column(String, unique=True, index=True, nullable=False)
    raw_content = Column(Text)
    tags = Column(JSON, default=[])
    topic_category = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    is_full_content = Column(Boolean, default=False)
    
    # AI Analysis Columns (Task 2.3)
    summary_vi = Column(Text, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    sentiment_label = Column(String, nullable=True)
    coins_mentioned = Column(JSON, default=[])
    key_events = Column(JSON, default=[])
    risk_level = Column(String, nullable=True)
    action_recommendation = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=True)  # Task 7.2: AI confidence
    
    # Phase 5: Truth Engine Columns
    category_type = Column(Enum(CategoryType), nullable=True)
    verification_status = Column(Enum(VerificationStatus), default=VerificationStatus.PENDING)
    evidence_data = Column(JSON, default={})
    
    # Task 5.6: Story Clustering
    cluster_id = Column(String(36), nullable=True, index=True)
    is_cluster_lead = Column(Boolean, default=False)
    
    # Task 5.7: Hotness Ranking
    ranking_score = Column(Float, default=0.0, index=True)    
    # Task 5.10: Editor's Choice / Pinned
    is_pinned = Column(Boolean, default=False)
    pinned_until = Column(DateTime(timezone=True), nullable=True)
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    source = relationship("app.models.source.Source")
    signal_correlation = relationship("NewsSignalCorrelation", back_populates="news", uselist=False)
