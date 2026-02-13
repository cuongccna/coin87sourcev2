"""Add pinned news columns"""
import asyncio
from app.db.session import engine
from sqlalchemy import text

async def add_pinned_columns():
    async with engine.begin() as conn:
        await conn.execute(text("ALTER TABLE news ADD COLUMN IF NOT EXISTS is_pinned BOOLEAN DEFAULT FALSE"))
        await conn.execute(text("ALTER TABLE news ADD COLUMN IF NOT EXISTS pinned_until TIMESTAMP"))
        print("✓ Pinned columns added")

if __name__ == "__main__":
    asyncio.run(add_pinned_columns())
