from fastapi import APIRouter, Depends, Query, Security, HTTPException
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, cast, String, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.models.news import News
from app.models.user import User
from app.schemas.news import NewsResponse, TrustBreakdown
from app.services.personalized_feed import PersonalizedFeedService

router = APIRouter()

API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_current_user_optional(
    api_key: str = Security(api_key_header),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get user if API key provided, None otherwise"""
    if not api_key:
        return None
    
    result = await db.execute(select(User).where(User.api_key == api_key))
    return result.scalars().first()

@router.get("/", response_model=List[NewsResponse])
async def read_news(
    skip: int = 0,
    limit: int = 100,
    topic: Optional[str] = None,
    sentiment: Optional[str] = None,
    coin: Optional[str] = None,
    risk: Optional[str] = None,
    sort: Optional[str] = Query("latest", regex="^(latest|trending)$"),  # Task 5.7
    db: AsyncSession = Depends(get_db)
):
    # Task 5.10: Get pinned news first (active pins only)
    # Eager load signal_correlation
    pinned_query = select(News).options(
        selectinload(News.signal_correlation)
    ).where(
        and_(
            News.is_pinned == True,
            or_(
                News.pinned_until == None,
                News.pinned_until > datetime.utcnow()
            )
        )
    ).order_by(desc(News.pinned_until))
    
    pinned_result = await db.execute(pinned_query)
    pinned_news = pinned_result.scalars().all()
    
    # Regular news query (exclude pinned to avoid duplicates)
    query = select(News).options(
        selectinload(News.signal_correlation)
    ).where(
        or_(
            News.is_pinned == False,
            and_(
                News.is_pinned == True,
                News.pinned_until <= datetime.utcnow()
            )
        )
    )
    
    # Task 5.7: Dynamic sorting
    if sort == "trending":
        query = query.order_by(desc(News.ranking_score))
    else:  # latest
        query = query.order_by(desc(News.published_at))
    
    if topic:
        query = query.where(News.topic_category == topic)
    
    if sentiment:
        query = query.where(News.sentiment_label == sentiment)

    if risk:
        query = query.where(News.risk_level == risk)
        
    # Dirty filter for coins in JSON String for MVP. 
    # Ideal: usage of Postgres JSONB operators or Full Text Search.
    if coin:
        # Assuming coins_mentioned is stored as '["BTC", "ETH"]'
        # We search for "BTC" inside the text representation.
        query = query.filter(cast(News.coins_mentioned, String).contains(f'"{coin.upper()}"'))

    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    regular_news = result.scalars().all()
    
    # Process enhanced trust for all news
    all_news = list(pinned_news) + list(regular_news)
    
    # Add enhanced trust to response
    for news in all_news:
        if news.signal_correlation:
            news.enhanced_trust_score = news.signal_correlation.enhanced_trust_score
            news.trust_breakdown = TrustBreakdown(
                base=news.signal_correlation.base_trust_score,
                smart_money_bonus=news.signal_correlation.smart_money_bonus,
                sentiment_bonus=news.signal_correlation.sentiment_bonus,
                onchain_bonus=news.signal_correlation.onchain_bonus
            )
    
    return all_news

@router.get("/feed", response_model=List[NewsResponse])
async def get_personalized_feed(
    feed_type: str = Query("for_you", regex="^(for_you|watchlist_only)$"),
    skip: int = 0,
    limit: int = 50,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Task 5.9: Personalized feed endpoint.
    - for_you: Boost ranking for watchlist matches (1.5x)
    - watchlist_only: Show only watchlist matches
    Requires X-API-KEY header.
    """
    if not current_user:
        # No auth, return general trending
        query = select(News).order_by(desc(News.ranking_score)).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    feed_service = PersonalizedFeedService(db)
    
    if feed_type == "watchlist_only":
        return await feed_service.get_watchlist_only_feed(current_user, skip, limit)
    else:  # for_you
        return await feed_service.get_personalized_feed(current_user, skip, limit)

@router.get("/{news_id}", response_model=NewsResponse)
async def get_single_news(
    news_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get single news article by ID"""
    result = await db.execute(
        select(News).options(
            selectinload(News.signal_correlation)
        ).where(News.id == news_id)
    )
    news = result.scalars().first()
    
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    # Add enhanced trust if available
    if news.signal_correlation:
        news.enhanced_trust_score = news.signal_correlation.enhanced_trust_score
        news.trust_breakdown = TrustBreakdown(
            base=news.signal_correlation.base_trust_score,
            smart_money_bonus=news.signal_correlation.smart_money_bonus,
            sentiment_bonus=news.signal_correlation.sentiment_bonus,
            onchain_bonus=news.signal_correlation.onchain_bonus
        )
    
    return news
