"""
Phase 5: Market Data Verification Service
Validates price/volume claims against real Binance market data
"""
import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.core.logger import log

class MarketVerifier:
    """
    Verifies market-related news claims using Binance API
    """
    
    BINANCE_BASE_URL = "https://api.binance.com/api/v3"
    
    @staticmethod
    async def check_market_reality(
        symbol: str,
        publish_time: datetime,
        sentiment: str,
        category_type: str
    ) -> Dict[str, Any]:
        """
        Verify market claims against actual data
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            publish_time: When the news was published
            sentiment: AI-detected sentiment (Bullish/Bearish)
            category_type: News category
            
        Returns:
            dict with verification_result, evidence, and market_data
        """
        # Only verify MARKET_MOVE category
        if category_type != "market_move":
            return {
                "verification_result": "NOT_APPLICABLE",
                "evidence": "Market verification only applies to MARKET_MOVE category",
                "market_data": {}
            }
        
        # Normalize symbol for Binance (e.g., BTC -> BTCUSDT)
        if not symbol.endswith("USDT"):
            symbol = f"{symbol}USDT"
        
        try:
            # Fetch 4-hour window AFTER publish time
            start_time = int(publish_time.timestamp() * 1000)
            end_time = int((publish_time + timedelta(hours=4)).timestamp() * 1000)
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Get kline (candlestick) data
                params = {
                    "symbol": symbol,
                    "interval": "1h",
                    "startTime": start_time,
                    "endTime": end_time,
                    "limit": 4
                }
                
                response = await client.get(
                    f"{MarketVerifier.BINANCE_BASE_URL}/klines",
                    params=params
                )
                
                if response.status_code != 200:
                    log.warning(f"Binance API error for {symbol}: {response.status_code}")
                    return {
                        "verification_result": "UNVERIFIABLE",
                        "evidence": f"Market data unavailable for {symbol}",
                        "market_data": {}
                    }
                
                klines = response.json()
                
                if not klines or len(klines) < 2:
                    return {
                        "verification_result": "UNVERIFIABLE",
                        "evidence": "Insufficient market data",
                        "market_data": {}
                    }
                
                # Calculate metrics
                first_candle = klines[0]
                last_candle = klines[-1]
                
                open_price = float(first_candle[1])
                close_price = float(last_candle[4])
                price_change_pct = ((close_price - open_price) / open_price) * 100
                
                # Volume analysis
                total_volume = sum(float(k[5]) for k in klines)
                avg_volume = total_volume / len(klines)
                
                # Get previous 4 hours for comparison
                prev_params = {
                    "symbol": symbol,
                    "interval": "1h",
                    "startTime": int((publish_time - timedelta(hours=4)).timestamp() * 1000),
                    "endTime": start_time,
                    "limit": 4
                }
                prev_response = await client.get(
                    f"{MarketVerifier.BINANCE_BASE_URL}/klines",
                    params=prev_params
                )
                
                volume_change_pct = 0
                if prev_response.status_code == 200:
                    prev_klines = prev_response.json()
                    if prev_klines:
                        prev_volume = sum(float(k[5]) for k in prev_klines) / len(prev_klines)
                        if prev_volume > 0:
                            volume_change_pct = ((avg_volume - prev_volume) / prev_volume) * 100
                
                # Verification logic
                market_data = {
                    "symbol": symbol,
                    "price_change_pct": round(price_change_pct, 2),
                    "volume_change_pct": round(volume_change_pct, 2),
                    "open_price": open_price,
                    "close_price": close_price
                }
                
                # Decision rules
                if sentiment == "Bullish":
                    if price_change_pct > 1 and volume_change_pct > 5:
                        result = "VERIFIED"
                        evidence = f"Bullish claim confirmed: {price_change_pct}% price increase, {volume_change_pct}% volume spike"
                    elif price_change_pct < -2:
                        result = "DEBUNKED"
                        evidence = f"Bullish claim contradicted: price dropped {price_change_pct}%"
                    else:
                        result = "NEUTRAL"
                        evidence = f"Bullish claim inconclusive: {price_change_pct}% price change"
                
                elif sentiment == "Bearish":
                    if price_change_pct < -1:
                        result = "VERIFIED"
                        evidence = f"Bearish claim confirmed: {price_change_pct}% price drop"
                    elif price_change_pct > 2:
                        result = "DEBUNKED"
                        evidence = f"Bearish claim contradicted: price rose {price_change_pct}%"
                    else:
                        result = "NEUTRAL"
                        evidence = f"Bearish claim inconclusive: {price_change_pct}% price change"
                else:
                    result = "NEUTRAL"
                    evidence = "Sentiment is neutral, no strong verification needed"
                
                log.info(f"Market verification for {symbol}: {result} - {evidence}")
                
                return {
                    "verification_result": result,
                    "evidence": evidence,
                    "market_data": market_data
                }
                
        except Exception as e:
            log.error(f"Market verification error for {symbol}: {str(e)}")
            return {
                "verification_result": "ERROR",
                "evidence": f"Verification failed: {str(e)}",
                "market_data": {}
            }
