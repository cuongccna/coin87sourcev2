from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import Optional
from app.db.session import get_db
from app.models.news import News
from app.models.user import User
from app.schemas.news import NewsResponse
from pydantic import BaseModel

router = APIRouter()

class PinRequest(BaseModel):
    duration_hours: int = 24  # Default 24h

ADMIN_EMAILS = ["admin@coin87.com", "tester@coin87.com"]  # Config later

async def get_admin_user(
    api_key: str,
    db: AsyncSession = Depends(get_db)
) -> User:
    """Verify admin access"""
    result = await db.execute(select(User).where(User.api_key == api_key))
    user = result.scalars().first()
    
    if not user or user.email not in ADMIN_EMAILS:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

@router.post("/news/{news_id}/pin", response_model=NewsResponse)
async def pin_news(
    news_id: int,
    pin_data: PinRequest,
    api_key: str,
    db: AsyncSession = Depends(get_db)
):
    """Pin news to top for specified duration (admin only)"""
    await get_admin_user(api_key, db)
    
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalars().first()
    
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    news.is_pinned = True
    news.pinned_until = datetime.utcnow() + timedelta(hours=pin_data.duration_hours)
    
    await db.commit()
    await db.refresh(news)
    return news

@router.delete("/news/{news_id}/pin", response_model=NewsResponse)
async def unpin_news(
    news_id: int,
    api_key: str,
    db: AsyncSession = Depends(get_db)
):
    """Unpin news (admin only)"""
    await get_admin_user(api_key, db)
    
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalars().first()
    
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    news.is_pinned = False
    news.pinned_until = None
    
    await db.commit()
    await db.refresh(news)
    return news
