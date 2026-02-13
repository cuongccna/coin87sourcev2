"""Test trending news endpoint"""
import asyncio
from app.services.ranking import HotnessRanking
from app.db.session import AsyncSessionLocal

async def test():
    async with AsyncSessionLocal() as db:
        news = await HotnessRanking.get_trending_news(db, limit=3)
        print(f'✅ Found {len(news)} trending news')
        for n in news:
            print(f'  #{n.id}: {n.title[:60]}... (score: {n.ranking_score})')

if __name__ == "__main__":
    asyncio.run(test())
