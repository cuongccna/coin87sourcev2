"""Add daily_free_unlocks to users table"""
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings

async def migrate():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        # Add new columns
        await conn.execute(text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS daily_free_unlocks INTEGER DEFAULT 10,
            ADD COLUMN IF NOT EXISTS last_free_unlock_reset TIMESTAMP WITH TIME ZONE DEFAULT NOW();
        """))
        
        # Update existing users with welcome bonus if they have 0 balance
        await conn.execute(text("""
            UPDATE users 
            SET balance = 1000.0, daily_free_unlocks = 10 
            WHERE balance < 10 AND tier = 'Free';
        """))
        
        print("✅ Migration completed: Added daily_free_unlocks and updated user balances")

if __name__ == "__main__":
    asyncio.run(migrate())
