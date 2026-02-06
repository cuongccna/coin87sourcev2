import asyncio
import aiohttp
import random
from fake_useragent import UserAgent
from typing import Optional, Dict

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
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            return await response.text()
                        elif response.status == 429: # Too Many Requests
                            wait_time = (2 ** attempt) + random.uniform(0, 1)
                            print(f"Rate limited. Waiting {wait_time:.2f}s...")
                            await asyncio.sleep(wait_time)
                        else:
                             # print(f"Fetch failed {url}: Status {response.status}")
                             break # Don't retry 404s etc.
            except Exception as e:
                # print(f"Network error {url}: {e}")
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                await asyncio.sleep(wait_time)
                
        return None
