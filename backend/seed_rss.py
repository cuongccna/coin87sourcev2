import asyncio
from app.db.session import AsyncSessionLocal
from app.models.source import Source, SourceType
from sqlalchemy import select

async def seed():
    async with AsyncSessionLocal() as db:
        # List of sources (Direct RSS or via Google News Wrapper for HTML pages)
        sources = [
            # Proven Crypto News RSS
            {"name": "CoinTelegraph RSS", "url": "https://cointelegraph.com/rss"},
            {"name": "Decrypt RSS", "url": "https://decrypt.co/feed"},
            {"name": "Kraken Blog", "url": "https://blog.kraken.com/feed"},
            {"name": "Bitfinex Blog", "url": "https://www.bitfinex.com/posts.rss"},
            
            # Exchange Announcements (Wrapped via Google News RSS for compatibility)
            {"name": "Binance Announcements", "url": "https://news.google.com/rss/search?q=site:binance.com/en/support/announcement+when:7d"},
            {"name": "OKX Announcements", "url": "https://news.google.com/rss/search?q=site:okx.com/help/category/announcements+when:7d"},
            {"name": "Bybit Announcements", "url": "https://news.google.com/rss/search?q=site:announcements.bybit.com+when:7d"},
            {"name": "Huobi/HTX Announcements", "url": "https://news.google.com/rss/search?q=site:htx.com/support+when:7d"},
            {"name": "KuCoin Announcements", "url": "https://news.google.com/rss/search?q=site:kucoin.com/announcement+when:7d"},
            {"name": "MEXC Announcements", "url": "https://news.google.com/rss/search?q=site:mexc.com/support+when:7d"},
            
            # Keep Coindesk but might fail
            {"name": "CoinDesk RSS", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/"}
        ]
        
        for s in sources:
            result = await db.execute(select(Source).where(Source.name == s["name"]))
            existing = result.scalars().first()
            
            if not existing:
                new_source = Source(
                    name=s["name"],
                    source_type=SourceType.rss,
                    config={"rss_url": s["url"]},
                    is_active=True
                )
                db.add(new_source)
                print(f"Added source: {s['name']}")
            else:
                print(f"Source already exists: {s['name']}")
        
        await db.commit()

if __name__ == "__main__":
    asyncio.run(seed())
