import asyncio
from app.db.session import engine
from app.models.vote import Vote
from app.models.user import User
from app.models.news import News
from app.models.base import Base

async def init_votes():
    async with engine.begin() as conn:
        await conn.run_sync(Vote.metadata.create_all)
    print("Vote table created.")

if __name__ == "__main__":
    asyncio.run(init_votes())
