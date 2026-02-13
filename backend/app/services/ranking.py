"""
Task 5.7: Hotness Ranking Algorithm
Tính điểm "Hot" cho tin tức (HackerNews/Reddit style)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.news import News
from app.models.source import Source
from app.models.vote import Vote
from app.core.logger import log
from datetime import datetime, timezone
from typing import Optional
import math

class HotnessRanking:
    """
    Tính toán và cập nhật ranking score cho tin tức
    Formula: Hot_Score = ((Trust * Impact) + (Votes * 2)) / (Age + 2)^1.5
    """
    
    GRAVITY = 1.5  # Độ "rơi" của tin cũ
    VOTE_MULTIPLIER = 2
    
    @staticmethod
    def calculate_age_in_hours(published_at: datetime) -> float:
        """Tính tuổi của tin tức (giờ)"""
        if published_at.tzinfo is None:
            published_at = published_at.replace(tzinfo=timezone.utc)
        
        now = datetime.now(timezone.utc)
        delta = now - published_at
        return max(0.1, delta.total_seconds() / 3600)  # Minimum 0.1h để tránh div/0
    
    @staticmethod
    async def calculate_hotness(news: News, db: AsyncSession) -> float:
        """
        Tính hotness score cho 1 tin
        
        Returns:
            float: Ranking score (0-1000+)
        """
        # 1. Trust Score (0-10) từ nguồn
        source_query = await db.execute(
            select(Source).where(Source.id == news.source_id)
        )
        source = source_query.scalar_one_or_none()
        trust_score = source.trust_score if source else 5.0
        
        # 2. Impact Score (0-10) từ AI sentiment
        # Map sentiment_score (-10 to +10) sang impact (0-10)
        # Tin có sentiment mạnh (bullish/bearish) = impact cao
        if news.sentiment_score is not None:
            impact_score = abs(news.sentiment_score)  # -10 hoặc +10 đều là high impact
        else:
            impact_score = 5.0  # Neutral default
        
        # 3. Vote Count (weighted by vote power)
        vote_count_query = select(func.count(Vote.id)).where(Vote.news_id == news.id)
        result = await db.execute(vote_count_query)
        vote_count = result.scalar() or 0
        
        # 4. Age Penalty
        age_hours = HotnessRanking.calculate_age_in_hours(news.published_at)
        
        # 5. Formula
        numerator = (trust_score * impact_score) + (vote_count * HotnessRanking.VOTE_MULTIPLIER)
        denominator = math.pow(age_hours + 2, HotnessRanking.GRAVITY)
        
        hotness = numerator / denominator
        
        return round(hotness, 2)
    
    @staticmethod
    async def update_all_scores(db: AsyncSession, time_window_hours: int = 72) -> int:
        """
        Cập nhật ranking score cho tất cả tin gần đây
        
        Args:
            time_window_hours: Chỉ update tin trong X giờ qua
        
        Returns:
            Số tin đã update
        """
        from datetime import timedelta
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
        
        # Lấy tin trong 72h qua
        query = select(News).where(News.published_at >= cutoff_time)
        result = await db.execute(query)
        news_items = result.scalars().all()
        
        updated_count = 0
        
        for news in news_items:
            try:
                new_score = await HotnessRanking.calculate_hotness(news, db)
                news.ranking_score = new_score
                updated_count += 1
            except Exception as e:
                log.error(f"Failed to calculate hotness for news {news.id}: {e}")
        
        await db.commit()
        
        log.info(f"Updated ranking scores for {updated_count} news items")
        return updated_count
    
    @staticmethod
    async def get_trending_news(
        db: AsyncSession, 
        limit: int = 20,
        offset: int = 0
    ) -> list[News]:
        """
        Lấy tin trending (sort by ranking_score DESC)
        """
        query = select(News).where(
            News.is_cluster_lead == True  # Chỉ lấy cluster leads
        ).order_by(
            News.ranking_score.desc()
        ).limit(limit).offset(offset)
        
        result = await db.execute(query)
        return result.scalars().all()
