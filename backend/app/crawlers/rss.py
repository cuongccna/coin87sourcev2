import asyncio
import feedparser
from typing import List, Dict, Any
from datetime import datetime
from app.crawlers.base import BaseCrawler
from app.services.content_processor import ContentProcessor
from app.services.normalizer import DateNormalizer

class RSSCrawler(BaseCrawler):
    async def fetch_data(self) -> List[Dict[str, Any]]:
        rss_url = self.config.get("rss_url")
from app.core.logger import log

class RSSCrawler(BaseCrawler):
    async def fetch_data(self) -> List[Dict[str, Any]]:
        rss_url = self.config.get("rss_url")
        if not rss_url:
            log.warning("No RSS URL configured")
            return []

        # Use NetworkClient to fetch the RSS content raw string first
        # This allows us to use proxies/User-Agent rotation
        raw_xml = await self.network.fetch(rss_url)
        if not raw_xml:
            # Fallback to feedparser default or just return empty
            # feedparser can fetch URL directly but less "Stealthy"
            # Let's try to parse the raw_xml string
            log.warning(f"Failed to fetch RSS XML from {rss_url}")
            return []

        # Run feedparser on the string content
        loop = asyncio.get_event_loop()
        feed = await loop.run_in_executor(None, feedparser.parse, raw_xml)
        
        if not feed.entries:
            log.warning(f"No entries found in RSS feed: {rss_url}")
            if feed.bozo:
                log.warning(f"Feedparser error: {feed.bozo_exception}")

        results = []
        for entry in feed.entries:
            # Task 1.8: Normalize Date
            raw_date = None
            if hasattr(entry, "published"): raw_date = entry.published
            elif hasattr(entry, "updated"): raw_date = entry.updated
            
            published_at = DateNormalizer.normalize_date(raw_date)

            # Extract content
            raw_content = entry.get("summary", "")
            if "content" in entry:
                raw_content = entry.content[0].value

            # TASK 1.4: CLEAN & FILTER
            cleaned_content = ContentProcessor.clean_text(raw_content)
            title = entry.get("title", "No Title")
            
            if not ContentProcessor.is_valid_candidate(title, cleaned_content):
                continue

            results.append({
                "title": title,
                "url": entry.get("link", ""),
                "published_at": published_at,
                "raw_content": cleaned_content
            })
            
        return results

