"""
Seed trading signals data for testing
"""
import asyncio
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.trading_signals import (
    TradingDecision, SmartMoneySignal, SentimentReport,
    OnChainIntelligence, WhaleAlert,
    RiskBand, SignalDirection, SignalBand, OnChainState, OnChainBias
)


async def seed_signals():
    """Seed sample trading signals data"""
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # 1. Trading Decision
        trading_decision = TradingDecision(
            overall_risk=42.5,
            risk_band=RiskBand.MODERATE,
            confidence=0.78,
            action="HOLD - Market showing mixed signals. Wait for clearer trend confirmation.",
            risk_components={
                "market_volatility": 55,
                "liquidity": 35,
                "news_sentiment": 48,
                "technical_indicators": 42,
                "volume_analysis": 38,
                "whale_activity": 62,
                "correlation_risk": 45,
                "regulatory_risk": 28
            },
            active_alerts=["High whale activity detected", "Volume spike on BTC"],
            bot_action="MONITOR",
            max_position_pct=15
        )
        session.add(trading_decision)
        
        # 2. Smart Money BTC
        smart_btc = SmartMoneySignal(
            coin="BTC",
            score=72,
            band=SignalBand.STRONG_BULLISH,
            direction=SignalDirection.BULLISH,
            confidence=0.82,
            timeframe="4H",
            modules_active=9,
            description_vi="Smart Money đang tích lũy BTC. 9/12 modules xác nhận tín hiệu mua mạnh với độ tin cậy 82%."
        )
        session.add(smart_btc)
        
        # 3. Smart Money ETH
        smart_eth = SmartMoneySignal(
            coin="ETH",
            score=65,
            band=SignalBand.WEAK_BULLISH,
            direction=SignalDirection.BULLISH,
            confidence=0.75,
            timeframe="4H",
            modules_active=8,
            description_vi="Smart Money ETH ở mức tích lũy. Áp lực mua trung bình với 8/12 modules hoạt động."
        )
        session.add(smart_eth)
        
        # 4. Sentiment BTC
        sentiment_btc = SentimentReport(
            coin="BTC",
            signal=SignalDirection.BULLISH,
            bullish_count=145,
            bearish_count=68,
            neutral_count=42,
            average_score=0.58,
            weighted_sentiment=0.62,
            velocity=12.5,
            sources={
                "twitter": 120,
                "reddit": 85,
                "news": 35,
                "telegram": 15
            }
        )
        session.add(sentiment_btc)
        
        # 5. Sentiment ETH
        sentiment_eth = SentimentReport(
            coin="ETH",
            signal=SignalDirection.NEUTRAL,
            bullish_count=98,
            bearish_count=92,
            neutral_count=55,
            average_score=0.51,
            weighted_sentiment=0.48,
            velocity=8.2,
            sources={
                "twitter": 95,
                "reddit": 72,
                "news": 48,
                "telegram": 30
            }
        )
        session.add(sentiment_eth)
        
        # 6. OnChain Intelligence
        onchain = OnChainIntelligence(
            state=OnChainState.ACTIVE,
            bias=OnChainBias.POSITIVE,
            score=68.5,
            confidence=0.85,
            whale_net_flow=125.8,
            whale_dominance=42.3,
            whale_tx_count=287,
            data_completeness=95.0,
            data_age_seconds=120,
            invariants_passed=True,
            use_recommendation=True,
            weight_multiplier=1.0
        )
        session.add(onchain)
        
        # 7. Whale Alerts
        whale_alerts = [
            WhaleAlert(
                alert_type="ACCUMULATION",
                net_flow=85.2,
                volume=1250.5,
                tx_count=45
            ),
            WhaleAlert(
                alert_type="ACCUMULATION",
                net_flow=42.8,
                volume=850.3,
                tx_count=28
            ),
            WhaleAlert(
                alert_type="DISTRIBUTION",
                net_flow=-28.5,
                volume=520.8,
                tx_count=18
            )
        ]
        for alert in whale_alerts:
            session.add(alert)
        
        await session.commit()
        print("Trading signals data seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_signals())
