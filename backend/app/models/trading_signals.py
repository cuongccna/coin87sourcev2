from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, Enum
from sqlalchemy.sql import func
from app.models.base import Base
import enum


class RiskBand(enum.Enum):
    SAFE = "SAFE"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


class SignalDirection(enum.Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


class SignalBand(enum.Enum):
    STRONG_BULLISH = "STRONG_BULLISH"
    WEAK_BULLISH = "WEAK_BULLISH"
    NEUTRAL = "NEUTRAL"
    WEAK_BEARISH = "WEAK_BEARISH"
    STRONG_BEARISH = "STRONG_BEARISH"


class OnChainState(enum.Enum):
    ACTIVE = "ACTIVE"
    DEGRADED = "DEGRADED"
    INACTIVE = "INACTIVE"


class OnChainBias(enum.Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"


class TradingDecision(Base):
    """Overall trading decision with risk components"""
    __tablename__ = "trading_decisions"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Overall metrics
    overall_risk = Column(Float, nullable=False)
    risk_band = Column(Enum(RiskBand), nullable=False)
    confidence = Column(Float, nullable=False)
    action = Column(String, nullable=False)  # AVOID, CAUTIOUS, NORMAL, AGGRESSIVE
    
    # Risk components (JSON array)
    risk_components = Column(JSON, default=[])
    
    # Quality metrics
    data_coverage = Column(Float, default=100.0)
    low_confidence_components = Column(JSON, default=[])
    
    # Recommendation
    bot_action = Column(String, nullable=False)  # HALT, REDUCE, NORMAL, AGGRESSIVE
    max_position_pct = Column(Float, default=0.0)
    
    # Alerts (JSON array of strings)
    active_alerts = Column(JSON, default=[])
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SmartMoneySignal(Base):
    """Smart money flow signals per coin"""
    __tablename__ = "smart_money_signals"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    coin = Column(String, nullable=False, index=True)  # BTC, ETH, etc.
    score = Column(Float, nullable=False)
    band = Column(Enum(SignalBand), nullable=False)
    direction = Column(Enum(SignalDirection), nullable=False)
    confidence = Column(Float, nullable=False)
    timeframe = Column(String, nullable=False)  # 1h, 4h, 1d
    modules_active = Column(Integer, default=0)
    modules_total = Column(Integer, default=8)
    
    # Vietnamese description
    description_vi = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SentimentReport(Base):
    """Social sentiment analysis per coin"""
    __tablename__ = "sentiment_reports"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    coin = Column(String, nullable=False, index=True)
    signal = Column(Enum(SignalDirection), nullable=False)
    
    # Message stats
    total_messages = Column(Integer, default=0)
    messages_analyzed = Column(Integer, default=0)
    bullish_count = Column(Integer, default=0)
    bearish_count = Column(Integer, default=0)
    neutral_count = Column(Integer, default=0)
    
    # Metrics
    average_score = Column(Float, default=0.0)
    weighted_sentiment = Column(Float, default=0.0)
    signal_strength = Column(Float, default=0.0)
    velocity = Column(Float, default=0.0)  # msg/min
    
    # Sources breakdown (JSON: {twitter: count, telegram: count, ...})
    sources = Column(JSON, default={})
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class OnChainIntelligence(Base):
    """OnChain metrics and whale activity"""
    __tablename__ = "onchain_intelligence"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    state = Column(Enum(OnChainState), nullable=False)
    bias = Column(Enum(OnChainBias), nullable=False)
    score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    
    # Active signals (JSON array)
    active_signals = Column(JSON, default=[])
    
    # Whale activity
    whale_net_flow = Column(Float, default=0.0)  # BTC
    whale_dominance = Column(Float, default=0.0)  # %
    whale_tx_count = Column(Integer, default=0)
    
    # Data quality
    data_completeness = Column(Float, default=100.0)
    data_age_seconds = Column(Integer, default=0)
    invariants_passed = Column(Boolean, default=True)
    
    # Recommendation
    use_recommendation = Column(Boolean, default=True)
    weight_multiplier = Column(Float, default=1.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WhaleAlert(Base):
    """Whale accumulation/distribution alerts"""
    __tablename__ = "whale_alerts"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    alert_type = Column(String, nullable=False)  # ACCUMULATION, DISTRIBUTION
    net_flow = Column(Float, nullable=False)  # BTC
    volume = Column(Float, nullable=False)
    tx_count = Column(Integer, default=0)
    dominance = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
