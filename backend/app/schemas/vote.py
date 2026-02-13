from pydantic import BaseModel
from datetime import datetime

class VoteCreate(BaseModel):
    vote_type: str  # 'trust' or 'fake'

class VoteResponse(BaseModel):
    id: int
    user_id: int
    news_id: int
    vote_type: str
    origin: str
    reward: float
    created_at: datetime

    class Config:
        from_attributes = True
