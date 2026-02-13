import asyncio
from app.db.session import engine
from sqlalchemy import inspect, text

async def check_schema():
    async with engine.connect() as conn:
        def get_columns(sync_conn):
            inspector = inspect(sync_conn)
            return [c['name'] for c in inspector.get_columns('news')]
        
        columns = await conn.run_sync(get_columns)
        print("News Table Columns:", columns)
        
        # Also check if summary_en is nullable
        # This is just a basic check

if __name__ == "__main__":
    asyncio.run(check_schema())
