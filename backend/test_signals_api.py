"""Test script for Trading Signals API"""
import asyncio
import httpx
import json

BASE_URL = "http://127.0.0.1:9010/api/v1/signals"

async def test_dashboard():
    """Test dashboard endpoint"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/dashboard", timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            print("=== TRADING SIGNALS DASHBOARD ===\n")
            
            # Trading Decision
            if data.get('trading_decision'):
                td = data['trading_decision']
                print(f"🎯 Trading Decision:")
                print(f"   Overall Risk: {td.get('overall_risk')}")
                print(f"   Risk Band: {td.get('risk_band')}")
                print(f"   Action: {td.get('action')}\n")
            
            # Smart Money BTC
            if data.get('smart_money_btc'):
                sm = data['smart_money_btc']
                print(f"💰 Smart Money BTC:")
                print(f"   Score: {sm.get('score')}")
                print(f"   Band: {sm.get('band')}")
                print(f"   Modules Active: {sm.get('modules_active')}\n")
            
            # Smart Money ETH
            if data.get('smart_money_eth'):
                sm = data['smart_money_eth']
                print(f"💰 Smart Money ETH:")
                print(f"   Score: {sm.get('score')}")
                print(f"   Band: {sm.get('band')}\n")
            
            # Sentiment BTC
            if data.get('sentiment_btc'):
                sent = data['sentiment_btc']
                print(f"📊 Sentiment BTC:")
                print(f"   Bullish: {sent.get('bullish_count')}")
                print(f"   Bearish: {sent.get('bearish_count')}")
                print(f"   Neutral: {sent.get('neutral_count')}\n")
            
            # OnChain Intelligence
            if data.get('onchain'):
                oc = data['onchain']
                print(f"⛓️  OnChain Intelligence:")
                print(f"   Whale Net Flow: {oc.get('whale_net_flow')}")
                print(f"   State: {oc.get('state')}")
                print(f"   Bias: {oc.get('bias')}\n")
            
            # Whale Alerts
            if data.get('whale_alerts'):
                print(f"🐋 Whale Alerts: {len(data['whale_alerts'])} alerts")
                for alert in data['whale_alerts'][:3]:
                    print(f"   - {alert.get('transaction_type')}: {alert.get('net_flow')} (Vol: {alert.get('volume')})")
            
            print("\n✅ Dashboard test PASSED")
            return True
            
        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP Error: {e.response.status_code}")
            print(f"Response: {e.response.text}")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

async def main():
    print("Testing Trading Signals API...\n")
    await test_dashboard()

if __name__ == "__main__":
    asyncio.run(main())
