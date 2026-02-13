"""
Task 5.6: News Clustering Service
Gom nhóm các tin tức giống nhau thành Story Clusters
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.news import News
from app.models.source import Source
from app.core.logger import log
from datetime import datetime, timedelta
from thefuzz import fuzz
import uuid

class NewsClusteringService:
    """
    Gom nhóm tin tức dựa trên độ tương đồng tiêu đề
    Chọn tin từ nguồn uy tín nhất làm cluster lead
    """
    
    SIMILARITY_THRESHOLD = 75  # 75% tương đồng
    TIME_WINDOW_HOURS = 6      # Cửa sổ thời gian để gom nhóm
    
    @staticmethod
    async def cluster_recent_news(db: AsyncSession) -> dict:
        """
        Chạy định kỳ để gom nhóm tin mới
        
        Returns:
            dict với thông tin số cluster tạo ra
        """
        cutoff_time = datetime.now() - timedelta(hours=NewsClusteringService.TIME_WINDOW_HOURS)
        
        # Lấy tin chưa được gom nhóm trong 6h qua
        unclustered_query = select(News).where(
            and_(
                News.cluster_id.is_(None),
                News.published_at >= cutoff_time
            )
        ).order_by(News.published_at.desc())
        
        result = await db.execute(unclustered_query)
        unclustered_news = result.scalars().all()
        
        if not unclustered_news:
            log.info("No unclustered news to process")
            return {"clusters_created": 0, "news_processed": 0}
        
        # Lấy tất cả cluster hiện có trong time window
        existing_clusters_query = select(News).where(
            and_(
                News.cluster_id.isnot(None),
                News.published_at >= cutoff_time
            )
        )
        
        existing_result = await db.execute(existing_clusters_query)
        existing_clustered = existing_result.scalars().all()
        
        # Map cluster_id -> list of news
        clusters = {}
        for news in existing_clustered:
            if news.cluster_id not in clusters:
                clusters[news.cluster_id] = []
            clusters[news.cluster_id].append(news)
        
        new_clusters = 0
        processed = 0
        
        for news in unclustered_news:
            processed += 1
            matched_cluster = None
            
            # Thử match với các cluster hiện có
            for cluster_id, cluster_items in clusters.items():
                for cluster_news in cluster_items:
                    similarity = fuzz.token_set_ratio(
                        news.title.lower(),
                        cluster_news.title.lower()
                    )
                    
                    if similarity >= NewsClusteringService.SIMILARITY_THRESHOLD:
                        matched_cluster = cluster_id
                        break
                
                if matched_cluster:
                    break
            
            if matched_cluster:
                # Thêm vào cluster hiện có
                news.cluster_id = matched_cluster
                clusters[matched_cluster].append(news)
                log.info(f"News {news.id} added to cluster {matched_cluster}")
            else:
                # Tạo cluster mới
                new_cluster_id = str(uuid.uuid4())
                news.cluster_id = new_cluster_id
                news.is_cluster_lead = True  # Tin đầu tiên làm lead
                clusters[new_cluster_id] = [news]
                new_clusters += 1
                log.info(f"Created new cluster {new_cluster_id} with news {news.id}")
        
        # Cập nhật cluster leads dựa trên trust_score
        await NewsClusteringService._update_cluster_leads(db, clusters)
        
        await db.commit()
        
        log.info(
            f"Clustering complete: {new_clusters} new clusters, "
            f"{processed} news processed"
        )
        
        return {
            "clusters_created": new_clusters,
            "news_processed": processed,
            "total_clusters": len(clusters)
        }
    
    @staticmethod
    async def _update_cluster_leads(db: AsyncSession, clusters: dict):
        """
        Chọn tin có trust_score cao nhất trong mỗi cluster làm lead
        """
        for cluster_id, cluster_items in clusters.items():
            # Lấy trust_score của từng nguồn
            news_with_scores = []
            
            for news in cluster_items:
                source_query = await db.execute(
                    select(Source).where(Source.id == news.source_id)
                )
                source = source_query.scalar_one_or_none()
                trust_score = source.trust_score if source else 0
                news_with_scores.append((news, trust_score))
            
            # Sort theo trust_score giảm dần
            news_with_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Set lead cho tin đầu tiên (highest trust)
            for i, (news, score) in enumerate(news_with_scores):
                news.is_cluster_lead = (i == 0)
    
    @staticmethod
    async def get_cluster_count(news_id: int, db: AsyncSession) -> int:
        """
        Đếm số tin trong cluster của một news item
        
        Returns:
            Số tin liên quan (không tính bản thân)
        """
        news_query = await db.execute(
            select(News).where(News.id == news_id)
        )
        news = news_query.scalar_one_or_none()
        
        if not news or not news.cluster_id:
            return 0
        
        count_query = select(func.count(News.id)).where(
            and_(
                News.cluster_id == news.cluster_id,
                News.id != news_id
            )
        )
        
        result = await db.execute(count_query)
        count = result.scalar()
        
        return count or 0
