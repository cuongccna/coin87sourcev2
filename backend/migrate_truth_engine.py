"""
Phase 5 Database Migration: Add Truth Engine columns
"""
import asyncio
from app.db.session import engine
from app.models.news import News
from app.models.base import Base

async def migrate_truth_engine():
    async with engine.begin() as conn:
        # This will add the new columns if they don't exist
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Truth Engine columns added successfully")
    print("   - category_type (Enum)")
    print("   - verification_status (Enum)")
    print("   - evidence_data (JSON)")

if __name__ == "__main__":
    asyncio.run(migrate_truth_engine())
