"""Personalized news feed service"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_, or_, func, cast, String
from typing import List, Optional
from app.models.news import News
from app.models.user import User

class PersonalizedFeedService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_personalized_feed(
        self,
        user: User,
        skip: int = 0,
        limit: int = 50
    ) -> List[News]:
        """
        Get personalized feed for user based on watchlist.
        News matching watchlist get 1.5x ranking boost.
        """
        if not user.watchlist:
            # No watchlist, return general trending
            query = select(News).order_by(desc(News.ranking_score)).offset(skip).limit(limit)
            result = await self.db.execute(query)
            return result.scalars().all()
        
        # Get all news sorted by base ranking
        query = select(News).order_by(desc(News.ranking_score)).limit(limit * 3)  # Fetch more to apply boost
        result = await self.db.execute(query)
        all_news = result.scalars().all()
        
        # Apply watchlist boost
        boosted_news = []
        for news in all_news:
            coins_mentioned = news.coins_mentioned or []
            
            # Check overlap with watchlist
            has_match = any(coin in user.watchlist for coin in coins_mentioned)
            
            if has_match:
                # Create pseudo-score for sorting (boost by 1.5x)
                boosted_score = (news.ranking_score or 0) * 1.5
            else:
                boosted_score = news.ranking_score or 0
            
            boosted_news.append((news, boosted_score))
        
        # Sort by boosted score
        boosted_news.sort(key=lambda x: x[1], reverse=True)
        
        # Return top items after skip
        final_news = [item[0] for item in boosted_news[skip:skip + limit]]
        return final_news
    
    async def get_watchlist_only_feed(
        self,
        user: User,
        skip: int = 0,
        limit: int = 50
    ) -> List[News]:
        """
        Get only news that match user's watchlist.
        Strict filtering.
        """
        if not user.watchlist:
            return []
        
        # Build OR conditions for each coin in watchlist
        # Using JSONB contains operator for efficient query
        query = select(News).order_by(desc(News.ranking_score))
        
        # Filter news where coins_mentioned array overlaps with watchlist
        conditions = []
        for coin in user.watchlist:
            # Check if coin exists in the JSONB array
            conditions.append(cast(News.coins_mentioned, String).contains(f'"{coin}"'))
        
        if conditions:
            query = query.where(or_(*conditions))
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
