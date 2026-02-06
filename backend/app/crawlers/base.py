from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.core.network import NetworkClient

class BaseCrawler(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        # Use a shared network client instance per crawler or global if needed.
        # For now, instance level is fine.
        self.network = NetworkClient()

    @abstractmethod
    async def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetches data from the source.
        Returns a list of dictionaries, each representing a news item.
        Expected keys in dict: 'title', 'url', 'published_at', 'raw_content'
        """
        pass
