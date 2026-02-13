import json
import google.generativeai as genai
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.logger import log
from app.core.prompts import CRYPTO_ANALYST_SYSTEM_PROMPT

class GeminiClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GeminiClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(
                model_name=settings.GEMINI_MODEL,
                system_instruction=CRYPTO_ANALYST_SYSTEM_PROMPT
            )
        else:
            log.warning("GEMINI_API_KEY not set. AI features disabled.")
            self.model = None

    async def analyze_content(self, title: str, content: str, source: str) -> Optional[Dict[str, Any]]:
        """
        Sends content to Gemini and retrieves structured JSON analysis.
        """
        if not self.model:
            return None

        # Prepare the input payload
        user_message = json.dumps({
            "title": title,
            "content": content[:10000], # Trucate to avoid context limit if extreme
            "source": source
        })

        try:
            # Generate content
            # Gemini Python SDK is synchronous for now in basic usage, 
            # but we can wrap it or use the async client if available.
            # For simplicity in this `async` function, we'll assume standard usage 
            # and might block slightly. Ideally run in executor.
            
            # Using generation_config to force JSON response if supported or just prompt engineering
            generation_config = genai.types.GenerationConfig(
               temperature=0.2,
               response_mime_type="application/json"
            )

            # To avoid blocking event loop
            import asyncio
            loop = asyncio.get_event_loop()
            
            response = await loop.run_in_executor(
                None, 
                lambda: self.model.generate_content(
                    user_message, 
                    generation_config=generation_config
                )
            )

            # Parse JSON
            try:
                result_json = json.loads(response.text)
                return result_json
            except json.JSONDecodeError:
                log.error(f"Failed to parse JSON from Gemini: {response.text}")
                return None

        except Exception as e:
            log.error(f"Gemini API Error: {e}")
            return None
