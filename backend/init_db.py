import asyncio
from app.db.session import engine
from app.models.base import Base
from app.models.source import Source
from app.models.news import News
from app.models.user import User
from app.models.vote import Vote
from app.models.transaction import Transaction
from app.models.trading_signals import TradingDecision, SmartMoneySignal, SentimentReport, OnChainIntelligence, WhaleAlert
from app.models.news_signal_correlation import NewsSignalCorrelation
from app.models.news_history import NewsHistory

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all) # Drop again to apply new AI columns
        await conn.run_sync(Base.metadata.create_all)
    print("Database Initialized")

if __name__ == "__main__":
    asyncio.run(init_db())
