from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserLogin, LoginResponse
import secrets

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalars().first()

    if not user:
        # Create new user with WELCOME BONUS
        new_api_key = secrets.token_urlsafe(32)
        user = User(
            email=user_in.email,
            api_key=new_api_key,
            tier="Free",
            balance=1000.0  # Welcome bonus: 1000 $C87
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    return LoginResponse(
        api_key=user.api_key,
        tier=user.tier,
        balance=user.balance
    )
