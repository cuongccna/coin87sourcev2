from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.vote import Vote  # Removed VoteOrigin import
from app.models.user import User
from app.models.news import News
from app.schemas.vote import VoteCreate, VoteResponse
from app.api.endpoints.users import get_current_user

router = APIRouter()

@router.get("/{news_id}/vote-status")
async def check_vote_status(
    news_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if current user has voted on this news"""
    result = await db.execute(
        select(Vote).where(Vote.user_id == current_user.id, Vote.news_id == news_id)
    )
    vote = result.scalars().first()
    if vote:
        return {"has_voted": True, "vote_type": vote.vote_type}
    return {"has_voted": False, "vote_type": None}

@router.post("/{news_id}/vote", response_model=VoteResponse)
async def vote_on_news(
    news_id: int,
    vote_in: VoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if news exists
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalars().first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    # Check if user already voted
    existing_vote = await db.execute(
        select(Vote).where(Vote.user_id == current_user.id, Vote.news_id == news_id)
    )
    if existing_vote.scalars().first():
        raise HTTPException(status_code=400, detail="Already voted on this news")
    
    # Validate vote_type
    if vote_in.vote_type not in ['trust', 'fake']:
        raise HTTPException(status_code=400, detail="Invalid vote_type")
    
    # Create vote
    new_vote = Vote(
        user_id=current_user.id,
        news_id=news_id,
        vote_type=vote_in.vote_type,
        origin="HUMAN"  # Store string value since DB column is VARCHAR
    )
    db.add(new_vote)
    
    # Reward user
    reward = 0.1  # Base reward for voting
    current_user.balance += reward
    
    await db.commit()
    await db.refresh(new_vote)
    
    return VoteResponse(
        id=new_vote.id,
        user_id=new_vote.user_id,
        news_id=new_vote.news_id,
        vote_type=new_vote.vote_type,
        origin=new_vote.origin,  # Already a string in DB
        reward=reward,
        created_at=new_vote.created_at
    )
