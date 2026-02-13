"""
Background job: Update ranking scores
Chạy mỗi 10 phút
"""
import asyncio
from app.db.session import AsyncSessionLocal
from app.services.ranking import HotnessRanking
from app.core.logger import log

async def update_ranking_scores():
    """
    Cập nhật ranking score cho tin trong 72h qua
    """
    async with AsyncSessionLocal() as db:
        log.info("Starting ranking score update job...")
        
        try:
            count = await HotnessRanking.update_all_scores(db, time_window_hours=72)
            log.info(f"Ranking update complete: {count} news items updated")
        except Exception as e:
            log.error(f"Ranking update failed: {e}")

if __name__ == "__main__":
    asyncio.run(update_ranking_scores())
