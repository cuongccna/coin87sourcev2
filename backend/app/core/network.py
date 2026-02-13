import asyncio
import aiohttp
import random
from fake_useragent import UserAgent
from typing import Optional, Dict

from app.core.logger import log

class NetworkClient:
    def __init__(self, timeout: int = 15, retries: int = 3):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.retries = retries
        self.ua = UserAgent()

    async def fetch(self, url: str) -> Optional[str]:
        """
        Fetch URL content with exponential backoff and random User-Agent.
        Returns HTML content string or None if failed.
        """
        for attempt in range(self.retries):
            headers = {
                "User-Agent": self.ua.random,
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "keep-alive"
            }
            try:
                log.debug(f"Fetching {url} (Attempt {attempt+1})")
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            return await response.text()
                        elif response.status == 429: # Too Many Requests
                            wait_time = (2 ** attempt) + random.uniform(0, 1)
                            log.warning(f"Rate limited {url}. Waiting {wait_time:.2f}s...")
                            await asyncio.sleep(wait_time)
                        else:
                             log.warning(f"Fetch failed {url}: Status {response.status}")
                             if response.status == 404 or response.status == 403:
                                 break # Don't retry
            except Exception as e:
                log.error(f"Network error {url}: {e}")
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                await asyncio.sleep(wait_time)
        
        log.error(f"Failed to fetch {url} after {self.retries} attempts.")
        return None
