import asyncio
import feedparser
from typing import List, Dict, Any
from datetime import datetime
from time import mktime
from app.crawlers.base import BaseCrawler
from app.services.content_processor import ContentProcessor

class RSSCrawler(BaseCrawler):
    async def fetch_data(self) -> List[Dict[str, Any]]:
        rss_url = self.config.get("rss_url")
        if not rss_url:
            print("No RSS URL configured")
            return []

        # Use NetworkClient to fetch the RSS content raw string first
        # This allows us to use proxies/User-Agent rotation
        raw_xml = await self.network.fetch(rss_url)
        if not raw_xml:
            # Fallback to feedparser default or just return empty
            # feedparser can fetch URL directly but less "Stealthy"
            # Let's try to parse the raw_xml string
            return []

        # Run feedparser on the string content
        loop = asyncio.get_event_loop()
        feed = await loop.run_in_executor(None, feedparser.parse, raw_xml)
        
        results = []
        for entry in feed.entries:
            # Extract published date
            published_at = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                 published_at = datetime.fromtimestamp(mktime(entry.published_parsed))
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                 published_at = datetime.fromtimestamp(mktime(entry.updated_parsed))
            else:
                 published_at = datetime.now()

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

