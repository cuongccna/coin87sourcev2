"""AI Cost Guard Service - Circuit Breaker for Budget Control"""
import redis.asyncio as redis
from datetime import datetime
from typing import Optional
from app.core.config import settings

class BudgetExceededException(Exception):
    """Raised when monthly budget is exceeded"""
    pass

class CostGuardService:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.monthly_limit_usd = 50.0  # $50/month limit
        
    async def connect(self):
        """Initialize Redis connection"""
        if not self.redis_client:
            self.redis_client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
    
    def _get_monthly_key(self) -> str:
        """Get Redis key for current month"""
        now = datetime.utcnow()
        return f"ai_cost:monthly:{now.year}_{now.month:02d}"
    
    async def estimate_cost(self, input_chars: int, output_chars: int) -> float:
        """Estimate API cost (Gemini pricing)"""
        # Gemini Flash pricing: ~$0.35 per 1M input tokens, ~$1.40 per 1M output tokens
        # Rough: 4 chars = 1 token
        input_tokens = input_chars / 4
        output_tokens = output_chars / 4
        
        input_cost = (input_tokens / 1_000_000) * 0.35
        output_cost = (output_tokens / 1_000_000) * 1.40
        
        return input_cost + output_cost
    
    async def check_budget(self) -> tuple[bool, float]:
        """Check if budget is available. Returns (can_proceed, current_cost)"""
        await self.connect()
        
        key = self._get_monthly_key()
        current_cost = await self.redis_client.get(key)
        current_cost = float(current_cost) if current_cost else 0.0
        
        can_proceed = current_cost < self.monthly_limit_usd
        return can_proceed, current_cost
    
    async def record_cost(self, cost: float):
        """Record API cost"""
        await self.connect()
        
        key = self._get_monthly_key()
        await self.redis_client.incrbyfloat(key, cost)
        await self.redis_client.expire(key, 60 * 60 * 24 * 35)  # 35 days TTL
    
    async def get_current_cost(self) -> float:
        """Get current month's total cost"""
        await self.connect()
        
        key = self._get_monthly_key()
        cost = await self.redis_client.get(key)
        return float(cost) if cost else 0.0

# Global instance
cost_guard = CostGuardService()
