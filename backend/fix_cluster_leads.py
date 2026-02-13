"""Fix: Set existing news as cluster leads"""
import asyncio
from app.db.session import engine
from sqlalchemy import text

async def fix():
    async with engine.begin() as conn:
        result = await conn.execute(text("UPDATE news SET is_cluster_lead = true WHERE cluster_id IS NULL"))
        print(f"✅ Updated {result.rowcount} news as cluster leads")

if __name__ == "__main__":
    asyncio.run(fix())
