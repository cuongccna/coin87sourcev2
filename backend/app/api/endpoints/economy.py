from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
from app.db.session import get_db
from app.models.user import User
from app.models.transaction import Transaction, TransactionType
from app.schemas.transaction import SpendRequest, TransactionResponse
from app.api.endpoints.users import get_current_user

router = APIRouter()

@router.post("/spend", response_model=TransactionResponse)
async def spend_tokens(
    spend_data: SpendRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Spend $C87 tokens for premium features"""
    
    # Define costs
    COSTS = {
        "unlock": 50,
        "boost": 100,
    }
    
    cost = COSTS.get(spend_data.spend_type)
    if not cost:
        raise HTTPException(status_code=400, detail="Invalid spend_type")
    
    # Check balance
    if current_user.balance < cost:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient balance. Need {cost} $C87, have {current_user.balance}"
        )
    
    # Deduct balance
    current_user.balance -= cost
    
    # Create transaction record
    transaction = Transaction(
        user_id=current_user.id,
        transaction_type=TransactionType.SPEND_UNLOCK if spend_data.spend_type == "unlock" else TransactionType.SPEND_BOOST,
        amount=-cost,
        balance_after=current_user.balance,
        related_news_id=spend_data.news_id,
        description=f"Spent {cost} $C87 for {spend_data.spend_type}"
    )
    
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    
    return transaction

@router.get("/balance")
async def get_balance(
    current_user: User = Depends(get_current_user)
):
    """Get current token balance"""
    return {
        "balance": current_user.balance,
        "tier": current_user.tier
    }

@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get transaction history for current user"""
    stmt = (
        select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .order_by(desc(Transaction.created_at))
        .limit(limit)
    )
    result = await db.execute(stmt)
    transactions = result.scalars().all()
    return transactions
