from typing import Dict, Any
from app.crawlers.base import BaseCrawler
from app.models.source import SourceType

class CrawlerFactory:
    @staticmethod
    def get_crawler(source_type: SourceType, config: Dict[str, Any]) -> BaseCrawler:
        if source_type == SourceType.rss:
            # We will implement RSSCrawler later, but for now we need runtime import to avoid circular dep issues if any,
            # or just import it here. Since RSSCrawler isn't created yet, we'll placeholder it.
            # However, prompt says "If source_type is 'rss', return an instance of RSSCrawler".
            # I must strictly follow the plan order. Task 1.3 is RSS.
            # But the factory needs to import it. I will defer the import inside the method or create a skeleton RSSCrawler if needed.
            # For this strict step, I'll return NotImplementedError as per "If 'twitter', raise NotImplementedError".
            # But for RSS, I should probably prepare it.
            # Let's create a stub for RSSCrawler in this step or just import it assuming it will exist.
            # Actually, `RSSCrawler` is Task 1.3. The instructions say "If source_type is 'rss', return an instance".
            # So I will assume the existence of `app.crawlers.rss.RSSCrawler` which allows me to write the factory code now.
            try:
                from app.crawlers.rss import RSSCrawler
                return RSSCrawler(config)
            except ImportError:
                 raise NotImplementedError("RSSCrawler not implemented yet.")
        
        elif source_type == SourceType.twitter:
             raise NotImplementedError("Twitter crawler not implemented yet.")
        
        else:
            raise ValueError(f"Unknown source type: {source_type}")
