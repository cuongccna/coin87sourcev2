"""Update vote origin column to use enum"""
import asyncio
from app.db.session import engine
from sqlalchemy import text

async def update_vote_origin():
    async with engine.begin() as conn:
        # Drop old column if exists
        await conn.execute(text("ALTER TABLE votes DROP COLUMN IF EXISTS origin CASCADE"))
        
        # Create enum type
        await conn.execute(text("""
            DO $$ BEGIN
                CREATE TYPE voteorigin AS ENUM ('HUMAN', 'SYSTEM_BOT');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))
        
        # Add new column with enum
        await conn.execute(text("ALTER TABLE votes ADD COLUMN origin voteorigin DEFAULT 'HUMAN'"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_votes_origin ON votes(origin)"))
        
        print("✓ Vote origin enum updated")

if __name__ == "__main__":
    asyncio.run(update_vote_origin())
