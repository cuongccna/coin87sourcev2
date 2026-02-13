"""Fix: Add clustering columns"""
import asyncio
from app.db.session import engine
from sqlalchemy import text

async def add_clustering_columns():
    async with engine.begin() as conn:
        await conn.execute(text("ALTER TABLE news ADD COLUMN IF NOT EXISTS cluster_id VARCHAR(36)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_news_cluster_id ON news(cluster_id)"))
        await conn.execute(text("ALTER TABLE news ADD COLUMN IF NOT EXISTS is_cluster_lead BOOLEAN DEFAULT false"))
        print("✅ Clustering columns added")

if __name__ == "__main__":
    asyncio.run(add_clustering_columns())
