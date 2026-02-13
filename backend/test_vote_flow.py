#!/usr/bin/env python
"""
Quick Test: Auth + Vote Flow
1. Login -> Get API Key
2. Fetch /news (ensure exists)
3. Vote on news
4. Check balance update
"""

import requests

API_BASE = "http://localhost:9010/api/v1"
TEST_EMAIL = "voter@coin87.com"

def test_full_flow():
    print("=== COIN87 Auth + Vote Integration Test ===\n")

    # 1. Login
    print("1. Login")
    res = requests.post(f"{API_BASE}/auth/login", json={"email": TEST_EMAIL})
    assert res.status_code == 200, f"Login failed: {res.text}"
    login_data = res.json()
    api_key = login_data["api_key"]
    initial_balance = login_data["balance"]
    print(f"   ✓ API Key: {api_key[:10]}...")
    print(f"   ✓ Initial Balance: ${initial_balance}\n")

    # 2. Fetch News
    print("2. Fetch News")
    res = requests.get(f"{API_BASE}/news?limit=1")
    assert res.status_code == 200, f"News fetch failed: {res.text}"
    news_list = res.json()
    if not news_list:
        print("   ✗ No news in DB. Run seed_rss.py first!")
        return
    news_id = news_list[0]["id"]
    print(f"   ✓ Found News ID: {news_id}\n")

    # 3. Vote
    print("3. Vote on News")
    headers = {"X-API-KEY": api_key}
    res = requests.post(f"{API_BASE}/news/{news_id}/vote", 
                        json={"vote_type": "trust"}, 
                        headers=headers)
    assert res.status_code == 200, f"Vote failed: {res.text}"
    vote_data = res.json()
    reward = vote_data["reward"]
    print(f"   ✓ Vote recorded. Reward: ${reward}\n")

    # 4. Check Profile
    print("4. Check Updated Profile")
    res = requests.get(f"{API_BASE}/users/me", headers=headers)
    assert res.status_code == 200, f"Profile fetch failed: {res.text}"
    profile = res.json()
    new_balance = profile["balance"]
    print(f"   ✓ New Balance: ${new_balance}")
    print(f"   ✓ Balance Increased: ${new_balance - initial_balance}\n")

    assert new_balance == initial_balance + reward, "Balance mismatch!"

    # 5. Try Double Vote (Should Fail)
    print("5. Try Double Vote")
    res = requests.post(f"{API_BASE}/news/{news_id}/vote", 
                        json={"vote_type": "fake"}, 
                        headers=headers)
    assert res.status_code == 400, "Double vote should be rejected"
    print(f"   ✓ Double vote rejected: {res.json()['detail']}\n")

    print("=== ALL TESTS PASSED ===")

if __name__ == "__main__":
    test_full_flow()
