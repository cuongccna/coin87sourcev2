import asyncio
from app.db.session import AsyncSessionLocal
from app.models.source import Source, SourceType

async def seed():
    async with AsyncSessionLocal() as db:
        # Example RSS Source: Coindesk
        source_name = "CoinDesk RSS"
        
        # Check if exists
        from sqlalchemy import select
        result = await db.execute(select(Source).where(Source.name == source_name))
        existing = result.scalars().first()
        
        if not existing:
            new_source = Source(
                name=source_name,
                source_type=SourceType.rss,
                config={"rss_url": "https://www.coindesk.com/arc/outboundfeeds/rss/"},
                is_active=True
            )
            db.add(new_source)
            await db.commit()
            print(f"Added source: {source_name}")
        else:
            print(f"Source already exists: {source_name}")

if __name__ == "__main__":
    asyncio.run(seed())
