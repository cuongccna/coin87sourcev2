import asyncio
from app.services.llm_client import GeminiClient

async def test_gemini():
    client = GeminiClient()
    
    print("Testing Gemini connection...")
    
    title = "Bitcoin hits $100k"
    content = "Bitcoin has finally reached the 100k milestone after months of anticipation."
    source = "Test Source"
    
    result = await client.analyze_content(title, content, source)
    
    if result:
        print("SUCCESS! Gemini Response:")
        print(result)
    else:
        print("FAILED to get response from Gemini.")

if __name__ == "__main__":
    asyncio.run(test_gemini())
