"""
Phase 5: Tier 1 Source Cross-Verification Service
Verifies news by checking if trusted (Tier 1) sources reported the same story
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from thefuzz import fuzz
from typing import Optional
from app.models.news import News
from app.models.source import Source
from app.core.logger import log

# Define Tier 1 source names (trusted authorities)
TIER_1_SOURCES = [
    "CoinTelegraph RSS",
    "CoinDesk RSS", 
    "Kraken Blog",
    "Decrypt RSS"
]

class Tier1Verifier:
    """
    Cross-checks news against Tier 1 sources for verification
    """
    
    @staticmethod
    async def verify_tier1_consensus(
        target_news: News,
        db: AsyncSession,
        similarity_threshold: int = 85
    ) -> tuple[bool, Optional[str]]:
        """
        Check if Tier 1 sources reported similar news
        
        Returns:
            (verified: bool, evidence: Optional[str])
        """
        # If the source itself is Tier 1, auto-verify
        source_query = await db.execute(select(Source).where(Source.id == target_news.source_id))
        source = source_query.scalar_one_or_none()
        
        if source and source.name in TIER_1_SOURCES:
            return (True, f"Direct from Tier 1 source: {source.name}")
        
        # Define time window: 2 hours before to 12 hours after
        time_start = target_news.published_at - timedelta(hours=2)
        time_end = target_news.published_at + timedelta(hours=12)
        
        # Get Tier 1 source IDs
        tier1_query = await db.execute(
            select(Source).where(Source.name.in_(TIER_1_SOURCES))
        )
        tier1_sources = tier1_query.scalars().all()
        tier1_ids = [s.id for s in tier1_sources]
        
        if not tier1_ids:
            log.warning("No Tier 1 sources found in database")
            return (False, None)
        
        # Query news from Tier 1 sources in the time window
        query = select(News).where(
            News.source_id.in_(tier1_ids),
            News.published_at >= time_start,
            News.published_at <= time_end
        )
        result = await db.execute(query)
        tier1_news = result.scalars().all()
        
        # Fuzzy match titles
        target_title = target_news.title.lower()
        for news in tier1_news:
            similarity = fuzz.token_set_ratio(target_title, news.title.lower())
            if similarity >= similarity_threshold:
                evidence = (
                    f"Confirmed by Tier 1 source '{news.source.name}' "
                    f"(similarity: {similarity}%). "
                    f"Title: '{news.title}'"
                )
                log.info(f"Tier 1 verification PASS for news {target_news.id}: {evidence}")
                return (True, evidence)
        
        log.info(f"Tier 1 verification PENDING for news {target_news.id}: No matching Tier 1 report found")
        return (False, None)
