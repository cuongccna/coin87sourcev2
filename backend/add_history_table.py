"""Add NewsHistory table"""
import asyncio
from app.db.session import engine
from sqlalchemy import text

async def add_history_table():
    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS news_history (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                news_id INTEGER NOT NULL REFERENCES news(id),
                version_number INTEGER NOT NULL,
                content_snapshot TEXT,
                ai_analysis_snapshot JSONB DEFAULT '{}',
                changed_by VARCHAR NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_news_history_news_id ON news_history(news_id)"))
        print("✓ NewsHistory table created")

if __name__ == "__main__":
    asyncio.run(add_history_table())
