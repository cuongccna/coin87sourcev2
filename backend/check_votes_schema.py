#!/usr/bin/env python
"""Check votes table schema"""
import asyncio
from app.db.session import AsyncSessionLocal
from sqlalchemy import text

async def check_schema():
    async with AsyncSessionLocal() as session:
        # Get column info for votes table
        result = await session.execute(text("""
            SELECT column_name, data_type, udt_name 
            FROM information_schema.columns 
            WHERE table_name = 'votes'
            ORDER BY ordinal_position;
        """))
        print("=== votes table schema ===")
        for row in result:
            print(f"  {row[0]}: {row[1]} ({row[2]})")

asyncio.run(check_schema())
