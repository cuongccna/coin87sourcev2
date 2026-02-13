"""
Background job: Verify PENDING news items
Run every 30 minutes
"""
import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.news import News, VerificationStatus
from app.services.truth_engine.orchestrator import TruthEngine
from app.core.logger import log
from datetime import datetime, timedelta

async def verify_pending_news():
    """
    Process all PENDING news items through Truth Engine
    """
    async with AsyncSessionLocal() as db:
        # Get news pending verification (published in last 7 days)
        cutoff_date = datetime.now() - timedelta(days=7)
        
        query = select(News).where(
            News.verification_status == VerificationStatus.PENDING,
            News.published_at >= cutoff_date
        ).limit(20)  # Process 20 at a time
        
        result = await db.execute(query)
        pending_news = result.scalars().all()
        
        log.info(f"Found {len(pending_news)} news items pending verification")
        
        truth_engine = TruthEngine()
        
        for news in pending_news:
            try:
                report = await truth_engine.verify_news(news, db)
                log.info(
                    f"Verified news {news.id}: "
                    f"{report['final_status']} (confidence: {report['confidence_score']}%)"
                )
            except Exception as e:
                log.error(f"Verification failed for news {news.id}: {e}")
        
        log.info("Background verification complete")

if __name__ == "__main__":
    asyncio.run(verify_pending_news())
