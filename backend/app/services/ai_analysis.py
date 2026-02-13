"""Enhanced AI Service with Confidence Score & Cost Guard"""
import google.generativeai as genai
from app.core.config import settings
from app.services.cost_guard import cost_guard, BudgetExceededException
from pydantic import BaseModel
from typing import List, Optional

class AIAnalysisResult(BaseModel):
    summary_vi: str
    sentiment_score: float  # -1.0 to 1.0
    sentiment_label: str  # Bullish/Bearish/Neutral
    coins_mentioned: List[str]
    key_events: List[str]
    risk_level: str  # Low/Medium/High
    action_recommendation: str
    confidence_score: float  # 0.0 to 1.0 (NEW)

class AIService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def analyze_news(self, title: str, content: str) -> AIAnalysisResult:
        """Analyze news with confidence score"""
        
        # Budget check
        can_proceed, current_cost = await cost_guard.check_budget()
        if not can_proceed:
            raise BudgetExceededException(
                f"Monthly budget exceeded: ${current_cost:.2f} / $50.00"
            )
        
        prompt = f"""Analyze this crypto news article. Provide ONLY a JSON response.

Title: {title}
Content: {content[:2000]}

Return JSON with:
- summary_vi: Vietnamese summary (max 200 chars)
- sentiment_score: -1.0 (bearish) to 1.0 (bullish)
- sentiment_label: "Bullish" / "Bearish" / "Neutral"
- coins_mentioned: Array of coin symbols (uppercase)
- key_events: Array of key events/dates
- risk_level: "Low" / "Medium" / "High"
- action_recommendation: Short advice
- confidence_score: 0.0 to 1.0 (how confident you are in this analysis)

If the article is vague, lacks data, or is opinion-based, set confidence_score < 0.6.
"""
        
        # Estimate cost
        input_chars = len(prompt)
        
        try:
            response = self.model.generate_content(prompt)
            output_text = response.text.strip()
            output_chars = len(output_text)
            
            # Record cost
            cost = await cost_guard.estimate_cost(input_chars, output_chars)
            await cost_guard.record_cost(cost)
            
            # Parse JSON
            import json
            # Remove markdown code blocks if present
            if output_text.startswith("```"):
                output_text = output_text.split("```")[1]
                if output_text.startswith("json"):
                    output_text = output_text[4:]
            
            data = json.loads(output_text.strip())
            return AIAnalysisResult(**data)
            
        except Exception as e:
            print(f"AI analysis error: {e}")
            # Fallback low-confidence result
            return AIAnalysisResult(
                summary_vi="Lỗi phân tích - cần xem lại thủ công",
                sentiment_score=0.0,
                sentiment_label="Neutral",
                coins_mentioned=[],
                key_events=[],
                risk_level="Unknown",
                action_recommendation="DYOR",
                confidence_score=0.0
            )

# Global instance
ai_service = AIService()
