"""
Service: Enhanced Trust Calculator
Tính toán enhanced trust score từ trading signals
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.news import News
from app.models.news_signal_correlation import NewsSignalCorrelation
from app.models.trading_signals import (
    SmartMoneySignal,
    SentimentReport,
    OnChainIntelligence
)


class EnhancedTrustCalculator:
    """Service để tính enhanced trust score cho news từ trading signals"""
    
    # Bullish keywords
    BULLISH_KEYWORDS = [
        "rally", "surge", "bullish", "gain", "rise", "pump", "moon",
        "breakout", "recovery", "growth", "bullrun",
        "tăng", "tích cực", "lạc quan", "bứt phá", "tăng trưởng"
    ]
    
    # Bearish keywords
    BEARISH_KEYWORDS = [
        "crash", "dump", "bearish", "fall", "drop", "decline", "plunge",
        "sell-off", "correction", "downturn", "bearmarket",
        "giảm", "sụt giảm", "bi quan", "rớt", "xuống", "giảm giá"
    ]
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @staticmethod
    def extract_keywords(title: str, content: str = "") -> List[str]:
        """Trích xuất sentiment keywords từ tin"""
        text = (title + " " + content).lower()
        keywords = []
        
        for keyword in EnhancedTrustCalculator.BULLISH_KEYWORDS:
            if keyword in text:
                keywords.append(keyword)
        
        for keyword in EnhancedTrustCalculator.BEARISH_KEYWORDS:
            if keyword in text:
                keywords.append(keyword)
        
        return keywords
    
    @staticmethod
    def is_bullish_news(keywords: List[str]) -> bool:
        """Kiểm tra tin có bullish không"""
        bullish_count = sum(1 for k in keywords if k in EnhancedTrustCalculator.BULLISH_KEYWORDS)
        bearish_count = sum(1 for k in keywords if k in EnhancedTrustCalculator.BEARISH_KEYWORDS)
        return bullish_count > bearish_count
    
    @staticmethod
    def is_bearish_news(keywords: List[str]) -> bool:
        """Kiểm tra tin có bearish không"""
        bullish_count = sum(1 for k in keywords if k in EnhancedTrustCalculator.BULLISH_KEYWORDS)
        bearish_count = sum(1 for k in keywords if k in EnhancedTrustCalculator.BEARISH_KEYWORDS)
        return bearish_count > bullish_count
    
    async def get_relevant_signals(
        self, 
        news_published_at: datetime,
        time_window_hours: int = 2
    ) -> Optional[Tuple[SmartMoneySignal, SentimentReport, OnChainIntelligence]]:
        """
        Lấy signals gần nhất trong time window
        
        Args:
            news_published_at: Thời điểm xuất bản tin
            time_window_hours: Khoảng thời gian tìm kiếm (±hours)
        
        Returns:
            Tuple (smart_money, sentiment, onchain) hoặc None
        """
        time_start = news_published_at - timedelta(hours=time_window_hours)
        time_end = news_published_at + timedelta(hours=time_window_hours)
        
        # Query smart money signal
        smart_money_query = select(SmartMoneySignal).where(
            and_(
                SmartMoneySignal.timestamp >= time_start,
                SmartMoneySignal.timestamp <= time_end
            )
        ).order_by(SmartMoneySignal.timestamp.desc()).limit(1)
        
        smart_money_result = await self.db.execute(smart_money_query)
        smart_money = smart_money_result.scalar_one_or_none()
        
        # Query sentiment report
        sentiment_query = select(SentimentReport).where(
            and_(
                SentimentReport.timestamp >= time_start,
                SentimentReport.timestamp <= time_end
            )
        ).order_by(SentimentReport.timestamp.desc()).limit(1)
        
        sentiment_result = await self.db.execute(sentiment_query)
        sentiment = sentiment_result.scalar_one_or_none()
        
        # Query onchain intelligence
        onchain_query = select(OnChainIntelligence).where(
            and_(
                OnChainIntelligence.timestamp >= time_start,
                OnChainIntelligence.timestamp <= time_end
            )
        ).order_by(OnChainIntelligence.timestamp.desc()).limit(1)
        
        onchain_result = await self.db.execute(onchain_query)
        onchain = onchain_result.scalar_one_or_none()
        
        # Chỉ return nếu có ít nhất 1 signal
        if smart_money or sentiment or onchain:
            return (smart_money, sentiment, onchain)
        
        return None
    
    def calculate_enhanced_trust(
        self,
        base_trust: float,
        smart_money: Optional[SmartMoneySignal],
        sentiment: Optional[SentimentReport],
        onchain: Optional[OnChainIntelligence],
        news_keywords: List[str]
    ) -> Dict[str, float]:
        """
        Tính enhanced trust score
        
        Args:
            base_trust: Trust score gốc từ Source (0-10)
            smart_money: Smart money signal
            sentiment: Sentiment report
            onchain: OnChain intelligence
            news_keywords: Keywords từ tin
        
        Returns:
            Dict với keys: enhanced_trust_score, smart_money_bonus, sentiment_bonus, onchain_bonus
        """
        smart_money_bonus = 0.0
        sentiment_bonus = 0.0
        onchain_bonus = 0.0
        
        # 1. Smart Money Bonus (-0.5 to +0.5)
        if smart_money:
            is_news_bullish = self.is_bullish_news(news_keywords)
            is_news_bearish = self.is_bearish_news(news_keywords)
            
            if smart_money.score >= 70:  # Strong bullish signal
                if is_news_bullish:
                    smart_money_bonus = +0.5
                elif is_news_bearish:
                    smart_money_bonus = -0.3  # Tin trái chiều
            elif smart_money.score <= 30:  # Strong bearish signal
                if is_news_bearish:
                    smart_money_bonus = +0.5
                elif is_news_bullish:
                    smart_money_bonus = -0.3  # Tin trái chiều
        
        # 2. Sentiment Bonus (-0.3 to +0.3)
        if sentiment and sentiment.total_messages > 0:
            bullish_ratio = sentiment.bullish_count / sentiment.total_messages
            is_news_bullish = self.is_bullish_news(news_keywords)
            is_news_bearish = self.is_bearish_news(news_keywords)
            
            if bullish_ratio > 0.6:  # Thị trường rất bullish
                if is_news_bullish:
                    sentiment_bonus = +0.3
                elif is_news_bearish:
                    sentiment_bonus = -0.2
            elif bullish_ratio < 0.4:  # Thị trường bearish
                if is_news_bearish:
                    sentiment_bonus = +0.3
                elif is_news_bullish:
                    sentiment_bonus = -0.2
        
        # 3. OnChain Bonus (0 to +0.2)
        if onchain and onchain.confidence:
            onchain_bonus = onchain.confidence * 0.2
        
        # Tính tổng
        enhanced_trust = base_trust + smart_money_bonus + sentiment_bonus + onchain_bonus
        
        # Clamp về [0, 10]
        enhanced_trust = max(0.0, min(10.0, enhanced_trust))
        
        return {
            "enhanced_trust_score": enhanced_trust,
            "smart_money_bonus": smart_money_bonus,
            "sentiment_bonus": sentiment_bonus,
            "onchain_bonus": onchain_bonus
        }
    
    async def process_news_article(
        self, 
        news: News,
        time_window_hours: int = 2
    ) -> Optional[NewsSignalCorrelation]:
        """
        Xử lý một tin tức: tìm signals và tính enhanced trust
        
        Args:
            news: News object
            time_window_hours: Khoảng thời gian tìm signals
        
        Returns:
            NewsSignalCorrelation object hoặc None nếu không có signals
        """
        # 1. Tìm signals
        signals = await self.get_relevant_signals(news.published_at, time_window_hours)
        
        if not signals:
            return None
        
        smart_money, sentiment, onchain = signals
        
        # 2. Extract keywords
        keywords = self.extract_keywords(news.title, news.raw_content or "")
        
        # 3. Tính enhanced trust
        base_trust = news.source.trust_score if news.source else 5.0
        trust_result = self.calculate_enhanced_trust(
            base_trust=base_trust,
            smart_money=smart_money,
            sentiment=sentiment,
            onchain=onchain,
            news_keywords=keywords
        )
        
        # 4. Tính time diff
        time_diff_seconds = None
        if smart_money:
            time_diff_seconds = int((smart_money.timestamp - news.published_at).total_seconds())
        elif sentiment:
            time_diff_seconds = int((sentiment.timestamp - news.published_at).total_seconds())
        elif onchain:
            time_diff_seconds = int((onchain.timestamp - news.published_at).total_seconds())
        
        # 5. Tạo correlation record
        correlation = NewsSignalCorrelation(
            news_id=news.id,
            smart_money_signal_id=smart_money.id if smart_money else None,
            sentiment_report_id=sentiment.id if sentiment else None,
            onchain_intelligence_id=onchain.id if onchain else None,
            enhanced_trust_score=trust_result["enhanced_trust_score"],
            base_trust_score=base_trust,
            smart_money_bonus=trust_result["smart_money_bonus"],
            sentiment_bonus=trust_result["sentiment_bonus"],
            onchain_bonus=trust_result["onchain_bonus"],
            time_diff_seconds=time_diff_seconds
        )
        
        return correlation
    
    async def batch_process_news(
        self, 
        news_list: List[News],
        time_window_hours: int = 2
    ) -> List[NewsSignalCorrelation]:
        """
        Xử lý batch nhiều tin cùng lúc
        
        Args:
            news_list: List of News objects
            time_window_hours: Khoảng thời gian tìm signals
        
        Returns:
            List of NewsSignalCorrelation objects
        """
        correlations = []
        
        for news in news_list:
            correlation = await self.process_news_article(news, time_window_hours)
            if correlation:
                correlations.append(correlation)
        
        return correlations
