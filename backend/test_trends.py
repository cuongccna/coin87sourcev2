"""Test trending narratives detection"""
import asyncio
from app.services.trends import TrendDetectionService
from app.db.session import AsyncSessionLocal

async def test():
    async with AsyncSessionLocal() as db:
        print("=== Testing Trending Narratives ===\n")
        
        narratives = await TrendDetectionService.detect_trending_narratives(db)
        
        if narratives:
            print(f"Found {len(narratives)} trending narratives:\n")
            for narrative in narratives[:5]:  # Top 5
                print(f"  Tag: {narrative['tag']}")
                print(f"     Velocity: {narrative['velocity']}x")
                print(f"     Count 24h: {narrative['count_24h']}")
                print(f"     Avg daily (7d): {narrative['avg_daily_7d']}")
                print(f"     Samples: {len(narrative['sample_news'])} news")
                print()
        else:
            print("No trending narratives detected (need more data)")
        
        print("\n=== Testing Trending Coins ===\n")
        
        coins = await TrendDetectionService.detect_trending_coins(db)
        
        if coins:
            print(f"Found {len(coins)} trending coins:\n")
            for coin in coins[:5]:
                print(f"  Coin: {coin['coin']}")
                print(f"     Velocity: {coin['velocity']}x")
                print(f"     Mentions 24h: {coin['count_24h']}")
                print()
        else:
            print("No trending coins detected")

if __name__ == "__main__":
    asyncio.run(test())
