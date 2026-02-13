"""
Task 5.8: Trends API endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from app.db.session import get_db
from app.services.trends import TrendDetectionService

router = APIRouter()

@router.get("/narratives", response_model=List[Dict[str, Any]])
async def get_trending_narratives(
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy danh sách narratives/topics đang trending
    
    Returns:
        List of trending tags với velocity > 2.0
    """
    return await TrendDetectionService.detect_trending_narratives(db)

@router.get("/coins", response_model=List[Dict[str, Any]])
async def get_trending_coins(
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy danh sách coins đang được mention nhiều
    
    Returns:
        List of trending coins với velocity > 2.0
    """
    return await TrendDetectionService.detect_trending_coins(db)
