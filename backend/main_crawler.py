import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.source import Source
from app.models.news import News
from app.crawlers.factory import CrawlerFactory
from app.services.deduplicator import DuplicateChecker
from app.services.tagger import KeywordTagger
from app.services.enricher import ContentEnricher
from app.services.llm_client import GeminiClient
from app.models.news import VerificationStatus, CategoryType
from app.core.logger import log

async def main():
    log.info("Starting Main Crawler...")
    
    # Initialize LLM Client
    llm_client = GeminiClient()

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
                
                # Reset failure count on success (Task 1.9)
                if source.consecutive_failures > 0:
                    source.consecutive_failures = 0
                    db.add(source)
                    await db.commit()

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

                    # 7. Enricher (Task 1.10)
                    # Use full text extraction if content is short
                    final_content = item["raw_content"]
                    image_url = None
                    is_full = False

                    if len(final_content) < 500:
                        # log.info(f"Enriching short content: {item['title']}")
                        enriched = ContentEnricher.enrich_news(item["url"])
                        if enriched.get("full_text"):
                            final_content = enriched["full_text"]
                            is_full = True
                        if enriched.get("image_url"):
                            image_url = enriched["image_url"]

                    # 8. AI Analysis (Task 2.3)
                    ai_data = {}
                    # Only analyze if we have content and it passes basic relevance
                    # We can use the 'tags' from Task 1.6 as a pre-filter if needed, 
                    # but let's let AI decide "is_relevant" too as per prompt.
                    # However, to save cost/latency, we might skip if it's very short and not enriched.
                    
                    log.info(f"Analyzing with AI: {item['title']}...")
                    analysis = await llm_client.analyze_content(item["title"], final_content, source.name)
                    
                    if analysis:
                        if analysis.get("is_relevant") is False:
                            log.info(f"AI marked as Irrelevant: {item['title']}")
                            continue # Skip saving if AI says irrelevant

                        ai_data = {
                            "summary_vi": analysis.get("summary_vi"),
                            "summary_en": analysis.get("summary_en"),
                            "sentiment_score": analysis.get("sentiment_score"),
                            "sentiment_label": analysis.get("sentiment_label"),
                            "coins_mentioned": analysis.get("coins_mentioned", []),
                            "key_events": analysis.get("key_events", []),
                            "risk_level": analysis.get("risk_level"),
                            "action_recommendation": analysis.get("action_recommendation")
                        }
                        
                        # Phase 5: Map category from AI (Task 5.2)
                        category_map = {
                            "market_move": CategoryType.MARKET_MOVE,
                            "project_update": CategoryType.PROJECT_UPDATE,
                            "partnership": CategoryType.PARTNERSHIP,
                            "security": CategoryType.SECURITY,
                            "opinion": CategoryType.OPINION
                        }
                        ai_data["category_type"] = category_map.get(
                            analysis.get("category", "opinion"),
                            CategoryType.OPINION
                        )
                    else:
                        verification_status=VerificationStatus.PENDING,  # Phase 5
                        log.warning(f"AI Analysis failed for {item['title']}")
                    
                    # 9. Save to DB
                    news = News(
                        source_id=source.id,
                        title=item["title"],
                        url=item["url"],
                        raw_content=final_content,
                        published_at=item["published_at"],
                        tags=tags, # Still keep rule-based tags as backup
                        topic_category=topic,
                        image_url=image_url,
                        is_full_content=is_full,
                        **ai_data
                    )
                    db.add(news)
                    new_count += 1
                
                await db.commit()
                log.info(f"Saved {new_count} new items.")

            except Exception as e:
                log.error(f"Error processing {source.name}: {e}")
                # Task 1.9: Circuit Breaker
                source.consecutive_failures += 1
                source.last_error_log = str(e)
                if source.consecutive_failures >= 5:
                    source.is_active = False
                    log.error(f"Source {source.name} disabled due to too many failures.")
                db.add(source)
                await db.commit()

if __name__ == "__main__":
    asyncio.run(main())
