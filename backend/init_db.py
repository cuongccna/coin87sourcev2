import asyncio
from app.db.session import engine
from app.models.base import Base
from app.models.source import Source
from app.models.news import News
from app.models.user import User

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all) # Drop again to apply new AI columns
        await conn.run_sync(Base.metadata.create_all)
    print("Database Initialized")

if __name__ == "__main__":
    asyncio.run(init_db())
