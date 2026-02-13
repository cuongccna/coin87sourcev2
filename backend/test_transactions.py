import asyncio
from app.db.session import get_db

async def check_transactions():
    async for db in get_db():
        result = await db.execute("SELECT COUNT(*) FROM transactions")
        count = result.scalar()
        print(f"Transactions count: {count}")
        break

asyncio.run(check_transactions())
