"""
Mock data: Tạo tin giả để test trending
"""
import asyncio
from datetime import datetime, timedelta, timezone
from app.db.session import AsyncSessionLocal
from app.models.news import News

async def create_mock_trending_news():
    """Tạo mock news với tags trùng lặp để test trending"""
    async with AsyncSessionLocal() as db:
        now = datetime.now(timezone.utc)
        
        # Create trending tag "AI" - 10 news in last 24h, 1 news in previous 7d
        for i in range(10):
            news = News(
                source_id=3,
                title=f"AI coin news #{i+1}",
                url=f"https://test.com/ai-{i+1}",
                raw_content="Test content",
                tags=["AI", "BTC"],
                coins_mentioned=["FET", "AGIX"],
                published_at=now - timedelta(hours=i),
                sentiment_label="Bullish"
            )
            db.add(news)
        
        # Old AI news (7 days ago) - để tính avg
        old_news = News(
            source_id=3,
            title="Old AI news",
            url="https://test.com/ai-old",
            raw_content="Old content",
            tags=["AI"],
            coins_mentioned=["FET"],
            published_at=now - timedelta(days=5),
            sentiment_label="Neutral"
        )
        db.add(old_news)
        
        # Create trending tag "DeFi" - 5 news in 24h, 0 in 7d (new narrative)
        for i in range(5):
            news = News(
                source_id=3,
                title=f"DeFi protocol #{i+1}",
                url=f"https://test.com/defi-{i+1}",
                raw_content="DeFi content",
                tags=["DeFi", "ETH"],
                coins_mentioned=["UNI", "AAVE"],
                published_at=now - timedelta(hours=i+2),
                sentiment_label="Bullish"
            )
            db.add(news)
        
        await db.commit()
        print("Created 16 mock news for trending test")

if __name__ == "__main__":
    asyncio.run(create_mock_trending_news())
