import asyncio
from app.db.session import engine
from app.models.base import Base
from app.models.source import Source
from app.models.news import News

async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Optional: Be careful
        await conn.run_sync(Base.metadata.create_all)
    print("Database Initialized")

if __name__ == "__main__":
    asyncio.run(init_db())
