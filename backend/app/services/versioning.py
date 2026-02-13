"""NewsHistory service for content versioning"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.news import News
from app.models.news_history import NewsHistory

class NewsVersionService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def save_snapshot(self, news: News, changed_by: str):
        """Save current state before updating"""
        # Get current version number
        result = await self.db.execute(
            select(func.max(NewsHistory.version_number))
            .where(NewsHistory.news_id == news.id)
        )
        max_version = result.scalar()
        next_version = (max_version or 0) + 1
        
        # Create snapshot
        snapshot = NewsHistory(
            news_id=news.id,
            version_number=next_version,
            content_snapshot=news.raw_content,
            ai_analysis_snapshot={
                "summary_vi": news.summary_vi,
                "sentiment_score": news.sentiment_score,
                "sentiment_label": news.sentiment_label,
                "coins_mentioned": news.coins_mentioned,
                "risk_level": news.risk_level,
                "action_recommendation": news.action_recommendation
            },
            changed_by=changed_by
        )
        
        self.db.add(snapshot)
        await self.db.commit()
        
        return next_version
    
    async def get_history(self, news_id: int):
        """Get version history for a news item"""
        result = await self.db.execute(
            select(NewsHistory)
            .where(NewsHistory.news_id == news_id)
            .order_by(NewsHistory.version_number.desc())
        )
        return result.scalars().all()
