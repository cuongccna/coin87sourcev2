from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.getcwd())

from app.main import app

client = TestClient(app)

def test_auth_and_user_flow():
    print("Testing Auth & User Flow...")
    
    # 1. Login/Sign up
    payload = {"email": "tester@coin87.com"}
    print(f"1. Login with {payload}")
    response = client.post("/api/v1/auth/login", json=payload)
    
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    print(f"   Success! Got API Key: {data['api_key'][:5]}... Tier: {data['tier']}")
    
    api_key = data['api_key']
    
    # 2. Get User Profile (/me)
    print(f"2. Fetching Profile with API Key")
    headers = {"X-API-KEY": api_key}
    response = client.get("/api/v1/users/me", headers=headers)
    
    assert response.status_code == 200, f"Get Profile failed: {response.text}"
    profile = response.json()
    print(f"   Success! Balance: {profile['balance']} $C87")
    assert profile['email'] == payload['email']
    
    # 3. Test Invalid Key
    print(f"3. Testing Invalid Key")
    response = client.get("/api/v1/users/me", headers={"X-API-KEY": "fake-key"})
    assert response.status_code == 403, "Should fail with 403"
    print("   Success! Access Denied as expected.")

if __name__ == "__main__":
    test_auth_and_user_flow()
