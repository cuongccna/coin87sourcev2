"""
Task 5.8: Trend Detection Service
Phát hiện chủ đề đang hot (Narrative Detection)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.news import News
from app.core.logger import log
from datetime import datetime, timedelta, timezone
from typing import Dict, List
from collections import Counter

class TrendDetectionService:
    """
    Phát hiện trending topics/narratives dựa trên velocity
    """
    
    VELOCITY_THRESHOLD = 2.0  # 200% increase = trending
    
    @staticmethod
    async def detect_trending_narratives(db: AsyncSession) -> List[Dict]:
        """
        Phát hiện tags/topics đang trending
        
        Returns:
            List[Dict]: [{"tag": "AI", "velocity": 3.5, "count_24h": 15, "sample_news": [...]}]
        """
        now = datetime.now(timezone.utc)
        day_ago = now - timedelta(hours=24)
        week_ago = now - timedelta(days=7)
        
        # Lấy tin 24h qua
        query_24h = select(News).where(News.published_at >= day_ago)
        result_24h = await db.execute(query_24h)
        news_24h = result_24h.scalars().all()
        
        # Lấy tin 7 ngày qua
        query_7d = select(News).where(
            and_(
                News.published_at >= week_ago,
                News.published_at < day_ago
            )
        )
        result_7d = await db.execute(query_7d)
        news_7d = result_7d.scalars().all()
        
        # Count tags trong 24h
        tags_24h = Counter()
        for news in news_24h:
            if news.tags:
                tags_list = news.tags if isinstance(news.tags, list) else []
                for tag in tags_list:
                    tags_24h[tag.upper()] += 1
        
        # Count tags trong 7d (để tính avg daily)
        tags_7d = Counter()
        for news in news_7d:
            if news.tags:
                tags_list = news.tags if isinstance(news.tags, list) else []
                for tag in tags_list:
                    tags_7d[tag.upper()] += 1
        
        # Calculate velocity
        trending_tags = []
        
        for tag, count_24h in tags_24h.items():
            if count_24h < 2:  # Skip tags với < 2 mentions
                continue
            
            # Avg daily count từ 7d trước đó
            avg_daily_7d = tags_7d.get(tag, 0) / 6  # 6 days (không tính 24h gần nhất)
            
            if avg_daily_7d == 0:
                # Tag mới xuất hiện = infinite velocity
                velocity = float('inf')
            else:
                velocity = (count_24h - avg_daily_7d) / avg_daily_7d
            
            if velocity >= TrendDetectionService.VELOCITY_THRESHOLD or avg_daily_7d == 0:
                # Lấy sample news
                sample_news = [
                    {
                        "id": n.id,
                        "title": n.title,
                        "sentiment_label": n.sentiment_label,
                        "published_at": n.published_at.isoformat()
                    }
                    for n in news_24h
                    if n.tags and tag in [t.upper() for t in (n.tags if isinstance(n.tags, list) else [])]
                ][:3]  # Top 3 samples
                
                trending_tags.append({
                    "tag": tag,
                    "velocity": round(velocity, 2) if velocity != float('inf') else 999.0,
                    "count_24h": count_24h,
                    "avg_daily_7d": round(avg_daily_7d, 1),
                    "sample_news": sample_news
                })
        
        # Sort by velocity DESC
        trending_tags.sort(key=lambda x: x["velocity"], reverse=True)
        
        log.info(f"Detected {len(trending_tags)} trending narratives")
        
        return trending_tags
    
    @staticmethod
    async def detect_trending_coins(db: AsyncSession) -> List[Dict]:
        """
        Phát hiện coins đang được mention nhiều (tương tự tags)
        """
        now = datetime.now(timezone.utc)
        day_ago = now - timedelta(hours=24)
        week_ago = now - timedelta(days=7)
        
        # Lấy tin 24h qua
        query_24h = select(News).where(News.published_at >= day_ago)
        result_24h = await db.execute(query_24h)
        news_24h = result_24h.scalars().all()
        
        # Lấy tin 7 ngày qua
        query_7d = select(News).where(
            and_(
                News.published_at >= week_ago,
                News.published_at < day_ago
            )
        )
        result_7d = await db.execute(query_7d)
        news_7d = result_7d.scalars().all()
        
        # Count coins
        coins_24h = Counter()
        for news in news_24h:
            if news.coins_mentioned:
                coins_list = news.coins_mentioned if isinstance(news.coins_mentioned, list) else []
                for coin in coins_list:
                    coins_24h[coin.upper()] += 1
        
        coins_7d = Counter()
        for news in news_7d:
            if news.coins_mentioned:
                coins_list = news.coins_mentioned if isinstance(news.coins_mentioned, list) else []
                for coin in coins_list:
                    coins_7d[coin.upper()] += 1
        
        # Calculate velocity
        trending_coins = []
        
        for coin, count_24h in coins_24h.items():
            if count_24h < 3:  # Coins cần ít nhất 3 mentions
                continue
            
            avg_daily_7d = coins_7d.get(coin, 0) / 6
            
            if avg_daily_7d == 0:
                velocity = 999.0  # New coin
            else:
                velocity = (count_24h - avg_daily_7d) / avg_daily_7d
            
            if velocity >= TrendDetectionService.VELOCITY_THRESHOLD or avg_daily_7d == 0:
                # Sample news
                sample_news = [
                    {
                        "id": n.id,
                        "title": n.title,
                        "sentiment_label": n.sentiment_label
                    }
                    for n in news_24h
                    if n.coins_mentioned and coin in [c.upper() for c in (n.coins_mentioned if isinstance(n.coins_mentioned, list) else [])]
                ][:3]
                
                trending_coins.append({
                    "coin": coin,
                    "velocity": round(velocity, 2) if velocity != 999.0 else 999.0,
                    "count_24h": count_24h,
                    "avg_daily_7d": round(avg_daily_7d, 1),
                    "sample_news": sample_news
                })
        
        trending_coins.sort(key=lambda x: x["velocity"], reverse=True)
        
        log.info(f"Detected {len(trending_coins)} trending coins")
        
        return trending_coins
