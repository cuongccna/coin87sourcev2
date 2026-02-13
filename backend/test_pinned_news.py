"""Test admin pinning functionality"""
import asyncio
import sys
sys.path.insert(0, 'D:/projects/coin87v2/coin87sourcev2/backend')

from app.db.session import AsyncSessionLocal
from app.models.news import News
from app.models.user import User
from sqlalchemy import select
from datetime import datetime, timedelta

async def test_pinning():
    async with AsyncSessionLocal() as db:
        # Get admin user
        result = await db.execute(select(User).where(User.email == "tester@coin87.com"))
        admin = result.scalars().first()
        
        if not admin:
            print("Admin user not found")
            return
        
        print(f"\n=== Admin User ===")
        print(f"Email: {admin.email}")
        print(f"API Key: {admin.api_key}")
        
        # Get first 3 news
        result = await db.execute(select(News).limit(3))
        news_list = result.scalars().all()
        
        if len(news_list) < 2:
            print("Not enough news for testing")
            return
        
        # Pin first news for 24h
        news_list[0].is_pinned = True
        news_list[0].pinned_until = datetime.utcnow() + timedelta(hours=24)
        
        # Pin second news for 1h
        news_list[1].is_pinned = True
        news_list[1].pinned_until = datetime.utcnow() + timedelta(hours=1)
        
        await db.commit()
        
        print(f"\n=== Pinned News ===")
        print(f"1. ID {news_list[0].id}: {news_list[0].title[:50]}... (24h)")
        print(f"2. ID {news_list[1].id}: {news_list[1].title[:50]}... (1h)")
        
        # Query all news with pinned first
        pinned_query = select(News).where(News.is_pinned == True).order_by(News.pinned_until.desc())
        result = await db.execute(pinned_query)
        pinned = result.scalars().all()
        
        regular_query = select(News).where(News.is_pinned == False).limit(5)
        result = await db.execute(regular_query)
        regular = result.scalars().all()
        
        print(f"\n=== News Listing (Pinned First) ===")
        print("--- Pinned ---")
        for news in pinned:
            print(f"[PINNED] ID {news.id}: {news.title[:60]}...")
            print(f"         Until: {news.pinned_until}")
        
        print("\n--- Regular ---")
        for idx, news in enumerate(regular[:3], 1):
            print(f"{idx}. ID {news.id}: {news.title[:60]}...")
        
        print(f"\n=== API Testing ===")
        print(f"Pin news: POST /api/v1/admin/news/{{id}}/pin?api_key={admin.api_key}")
        print(f"         Body: {{'duration_hours': 24}}")
        print(f"Unpin news: DELETE /api/v1/admin/news/{{id}}/pin?api_key={admin.api_key}")

if __name__ == "__main__":
    asyncio.run(test_pinning())
