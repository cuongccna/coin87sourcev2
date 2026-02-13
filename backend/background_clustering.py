"""
Task 5.6: Background job để chạy clustering
Chạy mỗi 10 phút
"""
import asyncio
from app.db.session import AsyncSessionLocal
from app.services.clustering import NewsClusteringService
from app.core.logger import log

async def run_clustering():
    """
    Chạy clustering cho tin tức mới
    """
    async with AsyncSessionLocal() as db:
        log.info("Starting news clustering job...")
        
        try:
            result = await NewsClusteringService.cluster_recent_news(db)
            log.info(f"Clustering result: {result}")
        except Exception as e:
            log.error(f"Clustering job failed: {e}")

if __name__ == "__main__":
    asyncio.run(run_clustering())
