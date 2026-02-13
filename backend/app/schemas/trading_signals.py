from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel


# Trading Decision Schemas
class RiskComponent(BaseModel):
    name: str
    weight: float
    score: float
    contribution: float
    confidence: float


class TradingDecisionBase(BaseModel):
    overall_risk: float
    risk_band: str
    confidence: float
    action: str
    risk_components: Dict[str, Any] = {}
    data_coverage: float = 100.0
    low_confidence_components: List[str] = []
    bot_action: str
    max_position_pct: float = 0.0
    active_alerts: List[str] = []


class TradingDecisionCreate(TradingDecisionBase):
    pass


class TradingDecisionResponse(TradingDecisionBase):
    id: int
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Smart Money Schemas
class SmartMoneySignalBase(BaseModel):
    coin: str
    score: float
    band: str
    direction: str
    confidence: float
    timeframe: str
    modules_active: int = 0
    modules_total: int = 8
    description_vi: Optional[str] = None


class SmartMoneySignalCreate(SmartMoneySignalBase):
    pass


class SmartMoneySignalResponse(SmartMoneySignalBase):
    id: int
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Sentiment Schemas
class SentimentReportBase(BaseModel):
    coin: str
    signal: str
    total_messages: int = 0
    messages_analyzed: int = 0
    bullish_count: int = 0
    bearish_count: int = 0
    neutral_count: int = 0
    average_score: float = 0.0
    weighted_sentiment: float = 0.0
    signal_strength: float = 0.0
    velocity: float = 0.0
    sources: Dict[str, int] = {}


class SentimentReportCreate(SentimentReportBase):
    pass


class SentimentReportResponse(SentimentReportBase):
    id: int
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# OnChain Schemas
class OnChainIntelligenceBase(BaseModel):
    state: str
    bias: str
    score: float
    confidence: float
    active_signals: List[str] = []
    whale_net_flow: float = 0.0
    whale_dominance: float = 0.0
    whale_tx_count: int = 0
    data_completeness: float = 100.0
    data_age_seconds: int = 0
    invariants_passed: bool = True
    use_recommendation: bool = True
    weight_multiplier: float = 1.0


class OnChainIntelligenceCreate(OnChainIntelligenceBase):
    pass


class OnChainIntelligenceResponse(OnChainIntelligenceBase):
    id: int
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Whale Alert Schemas
class WhaleAlertBase(BaseModel):
    alert_type: str
    net_flow: float
    volume: float
    tx_count: int = 0
    dominance: float = 0.0


class WhaleAlertCreate(WhaleAlertBase):
    pass


class WhaleAlertResponse(WhaleAlertBase):
    id: int
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Dashboard Summary Schema
class SignalsDashboard(BaseModel):
    """Combined dashboard with all signals"""
    trading_decision: Optional[TradingDecisionResponse] = None
    smart_money_btc: Optional[SmartMoneySignalResponse] = None
    smart_money_eth: Optional[SmartMoneySignalResponse] = None
    sentiment_btc: Optional[SentimentReportResponse] = None
    sentiment_eth: Optional[SentimentReportResponse] = None
    onchain: Optional[OnChainIntelligenceResponse] = None
    whale_alerts: List[WhaleAlertResponse] = []
