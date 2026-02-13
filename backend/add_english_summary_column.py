"""Add summary_en column"""
import asyncio
from app.db.session import engine
from sqlalchemy import text

async def add_english_summary_column():
    async with engine.begin() as conn:
        await conn.execute(text("ALTER TABLE news ADD COLUMN IF NOT EXISTS summary_en TEXT"))
        print("✓ summary_en column added")

if __name__ == "__main__":
    asyncio.run(add_english_summary_column())
