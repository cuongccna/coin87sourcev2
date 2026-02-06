from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime, timedelta
from thefuzz import fuzz
from app.models.news import News
from app.core.logger import log

class DuplicateChecker:
    @staticmethod
    async def is_duplicate(new_title: str, session: AsyncSession, threshold: int = 85) -> bool:
        """
        Check if the new_title is similar to any of the last 50 news titles 
        published in the last 24 hours.
        """
        if not new_title:
            return False

        # 1. Fetch recent news titles (last 24h, limit 50)
        yesterday = datetime.utcnow() - timedelta(days=1)
        stmt = (
            select(News.title)
            .where(News.published_at >= yesterday)
            .order_by(desc(News.published_at))
            .limit(50)
        )
        result = await session.execute(stmt)
        recent_titles = result.scalars().all()

        # 2. Compare using Fuzzy Logic
        for existing_title in recent_titles:
            # token_set_ratio is good for partial matches and reordered words
            score = fuzz.token_set_ratio(new_title, existing_title)
            if score > threshold:
                log.info(f"Duplicate detected! '{new_title}' is {score}% similar to '{existing_title}'")
                return True
                
        return False
