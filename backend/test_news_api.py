"""
Test API: Enhanced Trust Score
"""

import requests

# Test endpoint
url = "http://127.0.0.1:9010/api/v1/news"

try:
    response = requests.get(url, params={"limit": 2})
    response.raise_for_status()
    
    news_list = response.json()
    
    print(f"✅ GET /api/v1/news - Status: {response.status_code}\n")
    print(f"📰 Returned {len(news_list)} news articles\n")
    
    for news in news_list:
        print(f"ID: {news['id']}")
        print(f"Title: {news['title']}")
        print(f"Enhanced Trust: {news.get('enhanced_trust_score', 'N/A')}")
        
        if news.get('trust_breakdown'):
            print(f"  Breakdown:")
            print(f"    - Base: {news['trust_breakdown']['base']}")
            print(f"    - Smart Money: {news['trust_breakdown']['smart_money_bonus']:+.2f}")
            print(f"    - Sentiment: {news['trust_breakdown']['sentiment_bonus']:+.2f}")
            print(f"    - OnChain: {news['trust_breakdown']['onchain_bonus']:+.2f}")
        
        print()

except Exception as e:
    print(f"❌ Error: {e}")
