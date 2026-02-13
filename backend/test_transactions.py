import asyncio
from app.db.session import get_db
from sqlalchemy import text

async def check_transactions():
    async for db in get_db():
        result = await db.execute(text("SELECT COUNT(*) FROM transactions"))
        count = result.scalar()
        print(f"Transactions count: {count}")
        break

if __name__ == "__main__":
    asyncio.run(check_transactions())
