from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    pass

class UserLogin(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    api_key: str
    tier: str
    balance: float
    watchlist: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    api_key: str
    tier: str
    balance: float

class WatchlistUpdate(BaseModel):
    watchlist: List[str]
