"""
Test script: Enhanced Trust Calculator
"""

import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.news import News
from app.services.enhanced_trust_calculator import EnhancedTrustCalculator


async def test_enhanced_trust():
    """Test enhanced trust calculation"""
    
    async with AsyncSessionLocal() as db:
        # 1. Lấy một tin mới nhất (eager load source)
        from sqlalchemy.orm import selectinload
        query = select(News).options(selectinload(News.source)).order_by(News.published_at.desc()).limit(1)
        result = await db.execute(query)
        news = result.scalar_one_or_none()
        
        if not news:
            print("❌ Không có tin nào trong DB")
            return
        
        print(f"\n📰 Testing với tin: {news.title[:50]}...")
        print(f"   Published: {news.published_at}")
        print(f"   Source trust: {news.source.trust_score if news.source else 'N/A'}")
        
        # 2. Test keyword extraction
        calculator = EnhancedTrustCalculator(db)
        keywords = calculator.extract_keywords(news.title, news.raw_content or "")
        print(f"\n🔍 Keywords extracted: {keywords}")
        print(f"   Is bullish: {calculator.is_bullish_news(keywords)}")
        print(f"   Is bearish: {calculator.is_bearish_news(keywords)}")
        
        # 3. Test get relevant signals
        signals = await calculator.get_relevant_signals(news.published_at, time_window_hours=24)
        
        if signals:
            smart_money, sentiment, onchain = signals
            print(f"\n✅ Found signals:")
            if smart_money:
                print(f"   - Smart Money: score={smart_money.score}, timestamp={smart_money.timestamp}")
            if sentiment:
                print(f"   - Sentiment: bullish={sentiment.bullish_count}/{sentiment.total_messages}")
            if onchain:
                print(f"   - OnChain: confidence={onchain.confidence}")
        else:
            print(f"\n⚠️ Không tìm thấy signals trong time window 24h")
            print(f"   → Thử tạo fake signals cho test...")
            return
        
        # 4. Test calculate enhanced trust
        base_trust = news.source.trust_score if news.source else 5.0
        trust_result = calculator.calculate_enhanced_trust(
            base_trust=base_trust,
            smart_money=signals[0] if signals else None,
            sentiment=signals[1] if signals else None,
            onchain=signals[2] if signals else None,
            news_keywords=keywords
        )
        
        print(f"\n📊 Enhanced Trust Calculation:")
        print(f"   Base trust: {base_trust}")
        print(f"   Smart money bonus: {trust_result['smart_money_bonus']:+.2f}")
        print(f"   Sentiment bonus: {trust_result['sentiment_bonus']:+.2f}")
        print(f"   OnChain bonus: {trust_result['onchain_bonus']:+.2f}")
        print(f"   ────────────────────")
        print(f"   ENHANCED TRUST: {trust_result['enhanced_trust_score']:.2f}/10")
        
        # 5. Test process_news_article
        correlation = await calculator.process_news_article(news, time_window_hours=24)
        
        if correlation:
            print(f"\n✅ Correlation created:")
            print(f"   Enhanced trust: {correlation.enhanced_trust_score:.2f}")
            print(f"   Time diff: {correlation.time_diff_seconds}s")
            
            # Save to DB
            db.add(correlation)
            await db.commit()
            print(f"\n💾 Saved to database!")
        else:
            print(f"\n⚠️ Could not create correlation (no signals)")


if __name__ == "__main__":
    print("🧪 Testing Enhanced Trust Calculator\n")
    asyncio.run(test_enhanced_trust())
