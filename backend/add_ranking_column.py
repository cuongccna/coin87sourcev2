"""Add ranking_score column"""
import asyncio
from app.db.session import engine
from sqlalchemy import text

async def add_ranking_column():
    async with engine.begin() as conn:
        await conn.execute(text("ALTER TABLE news ADD COLUMN IF NOT EXISTS ranking_score FLOAT DEFAULT 0.0"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_news_ranking_score ON news(ranking_score DESC)"))
        print("✅ Ranking score column added")

if __name__ == "__main__":
    asyncio.run(add_ranking_column())
