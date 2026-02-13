from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse, WatchlistUpdate
from typing import List

router = APIRouter()

API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_current_user(
    api_key: str = Security(api_key_header),
    db: AsyncSession = Depends(get_db)
):
    if not api_key:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    
    result = await db.execute(select(User).where(User.api_key == api_key))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return user

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me/watchlist", response_model=UserResponse)
async def update_watchlist(
    watchlist_data: WatchlistUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user's watchlist (replace entire list)"""
    current_user.watchlist = watchlist_data.watchlist
    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.post("/me/watchlist/{coin_symbol}", response_model=UserResponse)
async def add_to_watchlist(
    coin_symbol: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a coin to watchlist"""
    coin_symbol = coin_symbol.upper()
    if current_user.watchlist is None:
        current_user.watchlist = []
    if coin_symbol not in current_user.watchlist:
        current_user.watchlist = current_user.watchlist + [coin_symbol]
        await db.commit()
        await db.refresh(current_user)
    return current_user

@router.delete("/me/watchlist/{coin_symbol}", response_model=UserResponse)
async def remove_from_watchlist(
    coin_symbol: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a coin from watchlist"""
    coin_symbol = coin_symbol.upper()
    if current_user.watchlist and coin_symbol in current_user.watchlist:
        current_user.watchlist = [c for c in current_user.watchlist if c != coin_symbol]
        await db.commit()
        await db.refresh(current_user)
    return current_user
