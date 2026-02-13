"""Add confidence_score column"""
import asyncio
from app.db.session import engine
from sqlalchemy import text

async def add_confidence_score():
    async with engine.begin() as conn:
        await conn.execute(text("ALTER TABLE news ADD COLUMN IF NOT EXISTS confidence_score FLOAT"))
        print("✓ confidence_score column added")

if __name__ == "__main__":
    asyncio.run(add_confidence_score())
