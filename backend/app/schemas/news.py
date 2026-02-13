from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel

class TrustBreakdown(BaseModel):
    """Breakdown của enhanced trust score"""
    base: float
    smart_money_bonus: float
    sentiment_bonus: float
    onchain_bonus: float
    
    class Config:
        from_attributes = True

class NewsBase(BaseModel):
    title: str
    url: str
    published_at: datetime
    tags: List[str] = []
    topic_category: Optional[str] = None
    image_url: Optional[str] = None
    
    # Content fields
    raw_content: Optional[str] = None

    # AI Fields
    summary_vi: Optional[str] = None
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    coins_mentioned: List[str] = []
    key_events: List[str] = []
    risk_level: Optional[str] = None
    action_recommendation: Optional[str] = None

class NewsResponse(NewsBase):
    id: int
    created_at: datetime
    
    # Task 5.7: Hotness ranking
    ranking_score: Optional[float] = None
    
    # Task 5.10: Pinned news
    is_pinned: bool = False
    pinned_until: Optional[datetime] = None
    
    # Enhanced Trust Score (from trading signals)
    enhanced_trust_score: Optional[float] = None
    trust_breakdown: Optional[TrustBreakdown] = None

    class Config:
        from_attributes = True
