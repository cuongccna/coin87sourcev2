"""Add transactions table"""
import asyncio
from app.db.session import engine
from sqlalchemy import text

async def add_transactions_table():
    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                transaction_type VARCHAR NOT NULL,
                amount FLOAT NOT NULL,
                balance_after FLOAT NOT NULL,
                related_news_id INTEGER REFERENCES news(id),
                description VARCHAR,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)"))
        print("✓ Transactions table created")

if __name__ == "__main__":
    asyncio.run(add_transactions_table())
