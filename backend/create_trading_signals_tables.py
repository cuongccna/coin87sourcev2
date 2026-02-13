"""Create trading signals tables

Revision ID: create_trading_signals
Revises: 
Create Date: 2026-02-07

"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.base import Base
from app.models.trading_signals import (
    TradingDecision, SmartMoneySignal, SentimentReport,
    OnChainIntelligence, WhaleAlert
)


async def upgrade():
    """Create trading signals tables"""
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        # Create all trading signals tables
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
    
    await engine.dispose()
    print("✅ Trading signals tables created successfully!")


async def downgrade():
    """Drop trading signals tables"""
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all, tables=[
            TradingDecision.__table__,
            SmartMoneySignal.__table__,
            SentimentReport.__table__,
            OnChainIntelligence.__table__,
            WhaleAlert.__table__,
        ])
    
    await engine.dispose()
    print("✅ Trading signals tables dropped!")


if __name__ == "__main__":
    print("🚀 Creating trading signals tables...")
    asyncio.run(upgrade())
