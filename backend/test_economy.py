import asyncio
import sys
from app.api.endpoints.economy import get_transactions
from app.api.endpoints.users import get_current_user
from app.db.session import get_db
from app.models.user import User
from sqlalchemy import select

async def test():
    # Get DB session
    async for db in get_db():
        # Get user
        result = await db.execute(
            select(User).where(User.api_key == "Dykrqhy1kVOTKkg23PyHpmMGRXnrewUPKhCC7zkm3_Y")
        )
        user = result.scalar_one_or_none()
        if not user:
            print("User not found")
            return
        
        print(f"User: {user.email}, balance: {user.balance}")
        
        # Test transactions
        transactions = await get_transactions(limit=20, current_user=user, db=db)
        print(f"Transactions: {len(transactions)}")
        for tx in transactions:
            print(f"  - {tx.transaction_type}: {tx.amount}")
        break

try:
    asyncio.run(test())
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
