from pydantic import BaseModel
from datetime import datetime

class SpendRequest(BaseModel):
    spend_type: str  # "unlock", "boost"
    news_id: int | None = None

class TransactionResponse(BaseModel):
    id: int
    transaction_type: str
    amount: float
    balance_after: float
    description: str | None = None
    created_at: datetime
    
    class Config:
        from_attributes = True
