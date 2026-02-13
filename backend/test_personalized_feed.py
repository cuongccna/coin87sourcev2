"""Test personalized feed with watchlist"""
import asyncio
import sys
sys.path.insert(0, 'D:/projects/coin87v2/coin87sourcev2/backend')

from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.news import News
from app.services.personalized_feed import PersonalizedFeedService
from sqlalchemy import select

async def test_personalized_feed():
    async with AsyncSessionLocal() as db:
        # Get first user
        result = await db.execute(select(User).limit(1))
        user = result.scalars().first()
        
        if not user:
            print("No user found. Create one first.")
            return
        
        print(f"\n=== User Info ===")
        print(f"Email: {user.email}")
        print(f"Current watchlist: {user.watchlist or []}")
        
        # Update watchlist for testing
        user.watchlist = ["BTC", "ETH", "AAVE"]
        await db.commit()
        print(f"Updated watchlist: {user.watchlist}")
        
        # Get all news to see what coins we have
        result = await db.execute(select(News).limit(20))
        all_news = result.scalars().all()
        print(f"\n=== Sample News (Total: {len(all_news)}) ===")
        for news in all_news[:5]:
            print(f"- {news.title[:60]}... | Coins: {news.coins_mentioned} | Score: {news.ranking_score}")
        
        # Test personalized feed (for_you)
        feed_service = PersonalizedFeedService(db)
        personalized = await feed_service.get_personalized_feed(user, skip=0, limit=10)
        
        print(f"\n=== Personalized Feed (for_you - boosted) ===")
        for idx, news in enumerate(personalized, 1):
            coins = news.coins_mentioned or []
            matches = [c for c in coins if c in user.watchlist]
            boost_indicator = " [BOOSTED 1.5x]" if matches else ""
            print(f"{idx}. {news.title[:60]}...")
            print(f"   Coins: {coins} | Matches: {matches}{boost_indicator}")
            print(f"   Base Score: {news.ranking_score}")
        
        # Test watchlist-only feed
        watchlist_only = await feed_service.get_watchlist_only_feed(user, skip=0, limit=10)
        
        print(f"\n=== Watchlist Only Feed ===")
        print(f"Found {len(watchlist_only)} news matching watchlist")
        for idx, news in enumerate(watchlist_only, 1):
            coins = news.coins_mentioned or []
            matches = [c for c in coins if c in user.watchlist]
            print(f"{idx}. {news.title[:60]}...")
            print(f"   Coins: {coins} | Matches: {matches}")

if __name__ == "__main__":
    asyncio.run(test_personalized_feed())
