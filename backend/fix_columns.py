"""Fix: Add missing columns directly"""
import asyncio
from app.db.session import engine
from sqlalchemy import text

async def add_columns():
    async with engine.begin() as conn:
        await conn.execute(text("ALTER TABLE news ADD COLUMN IF NOT EXISTS category_type categorytype"))
        await conn.execute(text("ALTER TABLE news ADD COLUMN IF NOT EXISTS verification_status verificationstatus DEFAULT 'PENDING'"))
        await conn.execute(text("ALTER TABLE news ADD COLUMN IF NOT EXISTS evidence_data JSONB"))
        print("✅ Phase 5 columns added")

if __name__ == "__main__":
    asyncio.run(add_columns())
