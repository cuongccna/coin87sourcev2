import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.source import Source
from app.models.news import News
from app.crawlers.factory import CrawlerFactory
from app.services.deduplicator import DuplicateChecker
from app.services.tagger import KeywordTagger
from app.core.logger import log

async def main():
    log.info("Starting Main Crawler...")
    
    async with AsyncSessionLocal() as db:
        # 1. Get active sources
        result = await db.execute(select(Source).where(Source.is_active == True))
        sources = result.scalars().all()
        
        if not sources:
            log.warning("No active sources found.")
            return

        for source in sources:
            log.info(f"Processing Source: {source.name} ({source.source_type})")
            
            try:
                # 2. Instantiate Crawler
                crawler = CrawlerFactory.get_crawler(source.source_type, source.config)
                
                # 3. Fetch Data
                items = await crawler.fetch_data()
                log.info(f"Fetched {len(items)} items from {source.name}")
                
                new_count = 0
                for item in items:
                    # 4. Check Duplicates (by URL)
                    existing = await db.execute(select(News).where(News.url == item["url"]))
                    if existing.scalars().first():
                        continue 

                    # 5. Fuzzy Check
                    if await DuplicateChecker.is_duplicate(item["title"], db):
                        continue
                    
                    # 6. Tagger & Noise Filter (Task 1.6)
                    full_text = f"{item['title']} {item['raw_content']}"
                    if not KeywordTagger.is_relevant(full_text):
                        # log.info(f"Skipped irrelevent: {item['title']}")
                        continue
                    
                    tags, topic = KeywordTagger.extract_tags(full_text)

                    # 7. Save to DB
                    news = News(
                        source_id=source.id,
                        title=item["title"],
                        url=item["url"],
                        raw_content=item["raw_content"],
                        published_at=item["published_at"],
                        tags=tags,
                        topic_category=topic
                    )
                    db.add(news)
                    new_count += 1
                
                await db.commit()
                log.info(f"Saved {new_count} new items.")

            except Exception as e:
                log.error(f"Error processing {source.name}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
