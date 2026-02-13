"""Add watchlist column to users table"""
import asyncio
from app.db.session import engine
from sqlalchemy import text

async def add_watchlist():
    async with engine.begin() as conn:
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS watchlist JSONB DEFAULT '[]'"))
        print("✓ Watchlist column added")

if __name__ == "__main__":
    asyncio.run(add_watchlist())
