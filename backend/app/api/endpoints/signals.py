from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.models.trading_signals import (
    TradingDecision, SmartMoneySignal, SentimentReport,
    OnChainIntelligence, WhaleAlert
)
from app.schemas.trading_signals import (
    TradingDecisionCreate, TradingDecisionResponse,
    SmartMoneySignalCreate, SmartMoneySignalResponse,
    SentimentReportCreate, SentimentReportResponse,
    OnChainIntelligenceCreate, OnChainIntelligenceResponse,
    WhaleAlertCreate, WhaleAlertResponse,
    SignalsDashboard
)

router = APIRouter()


# Trading Decision Endpoints
@router.post("/trading-decision", response_model=TradingDecisionResponse)
async def create_trading_decision(
    decision: TradingDecisionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new trading decision (for bot ingest)"""
    db_decision = TradingDecision(**decision.model_dump())
    db.add(db_decision)
    await db.commit()
    await db.refresh(db_decision)
    return db_decision


@router.get("/trading-decision/latest", response_model=TradingDecisionResponse)
async def get_latest_trading_decision(db: AsyncSession = Depends(get_db)):
    """Get latest trading decision"""
    result = await db.execute(
        select(TradingDecision).order_by(desc(TradingDecision.timestamp)).limit(1)
    )
    decision = result.scalars().first()
    if not decision:
        raise HTTPException(status_code=404, detail="No trading decision found")
    return decision


# Smart Money Endpoints
@router.post("/smart-money", response_model=SmartMoneySignalResponse)
async def create_smart_money_signal(
    signal: SmartMoneySignalCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new smart money signal"""
    db_signal = SmartMoneySignal(**signal.model_dump())
    db.add(db_signal)
    await db.commit()
    await db.refresh(db_signal)
    return db_signal


@router.get("/smart-money/{coin}", response_model=SmartMoneySignalResponse)
async def get_smart_money_signal(coin: str, db: AsyncSession = Depends(get_db)):
    """Get latest smart money signal for a coin"""
    result = await db.execute(
        select(SmartMoneySignal)
        .where(SmartMoneySignal.coin == coin.upper())
        .order_by(desc(SmartMoneySignal.timestamp))
        .limit(1)
    )
    signal = result.scalars().first()
    if not signal:
        raise HTTPException(status_code=404, detail=f"No signal found for {coin}")
    return signal


@router.get("/smart-money", response_model=List[SmartMoneySignalResponse])
async def get_all_smart_money_signals(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get recent smart money signals (all coins)"""
    result = await db.execute(
        select(SmartMoneySignal)
        .order_by(desc(SmartMoneySignal.timestamp))
        .limit(limit)
    )
    return result.scalars().all()


# Sentiment Endpoints
@router.post("/sentiment", response_model=SentimentReportResponse)
async def create_sentiment_report(
    report: SentimentReportCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new sentiment report"""
    db_report = SentimentReport(**report.model_dump())
    db.add(db_report)
    await db.commit()
    await db.refresh(db_report)
    return db_report


@router.get("/sentiment/{coin}", response_model=SentimentReportResponse)
async def get_sentiment_report(coin: str, db: AsyncSession = Depends(get_db)):
    """Get latest sentiment report for a coin"""
    result = await db.execute(
        select(SentimentReport)
        .where(SentimentReport.coin == coin.upper())
        .order_by(desc(SentimentReport.timestamp))
        .limit(1)
    )
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail=f"No sentiment report found for {coin}")
    return report


# OnChain Endpoints
@router.post("/onchain", response_model=OnChainIntelligenceResponse)
async def create_onchain_intelligence(
    intel: OnChainIntelligenceCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new onchain intelligence report"""
    db_intel = OnChainIntelligence(**intel.model_dump())
    db.add(db_intel)
    await db.commit()
    await db.refresh(db_intel)
    return db_intel


@router.get("/onchain/latest", response_model=OnChainIntelligenceResponse)
async def get_latest_onchain_intelligence(db: AsyncSession = Depends(get_db)):
    """Get latest onchain intelligence"""
    result = await db.execute(
        select(OnChainIntelligence).order_by(desc(OnChainIntelligence.timestamp)).limit(1)
    )
    intel = result.scalars().first()
    if not intel:
        raise HTTPException(status_code=404, detail="No onchain intelligence found")
    return intel


# Whale Alert Endpoints
@router.post("/whale-alert", response_model=WhaleAlertResponse)
async def create_whale_alert(
    alert: WhaleAlertCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new whale alert"""
    db_alert = WhaleAlert(**alert.model_dump())
    db.add(db_alert)
    await db.commit()
    await db.refresh(db_alert)
    return db_alert


@router.get("/whale-alerts", response_model=List[WhaleAlertResponse])
async def get_whale_alerts(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get recent whale alerts"""
    result = await db.execute(
        select(WhaleAlert).order_by(desc(WhaleAlert.timestamp)).limit(limit)
    )
    return result.scalars().all()


# Dashboard Endpoint (Combined)
@router.get("/dashboard", response_model=SignalsDashboard)
async def get_signals_dashboard(db: AsyncSession = Depends(get_db)):
    """Get combined signals dashboard"""
    
    # Get latest trading decision
    td_result = await db.execute(
        select(TradingDecision).order_by(desc(TradingDecision.timestamp)).limit(1)
    )
    trading_decision = td_result.scalars().first()
    
    # Get smart money signals (BTC, ETH)
    sm_btc_result = await db.execute(
        select(SmartMoneySignal)
        .where(SmartMoneySignal.coin == "BTC")
        .order_by(desc(SmartMoneySignal.timestamp))
        .limit(1)
    )
    smart_money_btc = sm_btc_result.scalars().first()
    
    sm_eth_result = await db.execute(
        select(SmartMoneySignal)
        .where(SmartMoneySignal.coin == "ETH")
        .order_by(desc(SmartMoneySignal.timestamp))
        .limit(1)
    )
    smart_money_eth = sm_eth_result.scalars().first()
    
    # Get sentiment reports (BTC, ETH)
    sent_btc_result = await db.execute(
        select(SentimentReport)
        .where(SentimentReport.coin == "BTC")
        .order_by(desc(SentimentReport.timestamp))
        .limit(1)
    )
    sentiment_btc = sent_btc_result.scalars().first()
    
    sent_eth_result = await db.execute(
        select(SentimentReport)
        .where(SentimentReport.coin == "ETH")
        .order_by(desc(SentimentReport.timestamp))
        .limit(1)
    )
    sentiment_eth = sent_eth_result.scalars().first()
    
    # Get latest onchain intelligence
    oc_result = await db.execute(
        select(OnChainIntelligence).order_by(desc(OnChainIntelligence.timestamp)).limit(1)
    )
    onchain = oc_result.scalars().first()
    
    # Get recent whale alerts
    wa_result = await db.execute(
        select(WhaleAlert).order_by(desc(WhaleAlert.timestamp)).limit(5)
    )
    whale_alerts = wa_result.scalars().all()
    
    return SignalsDashboard(
        trading_decision=trading_decision,
        smart_money_btc=smart_money_btc,
        smart_money_eth=smart_money_eth,
        sentiment_btc=sentiment_btc,
        sentiment_eth=sentiment_eth,
        onchain=onchain,
        whale_alerts=whale_alerts
    )
