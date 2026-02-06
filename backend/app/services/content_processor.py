import re
from bs4 import BeautifulSoup
from typing import List

class ContentProcessor:
    BLACKLIST_KEYWORDS = [
        "Login", "Subscribe", "Privacy Policy", "Casino", "Betting", 
        "Terms of Service", "Sign up", "Advertisement", "Click here"
    ]

    @staticmethod
    def clean_text(html_content: str) -> str:
        """
        Remove all HTML tags, <script>, <style>.
        Collapse multiple spaces/newlines into single ones.
        Trim leading/trailing whitespace.
        """
        if not html_content:
            return ""
        
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        text = soup.get_text(separator=" ")
        
        # Collapse multiple spaces and newlines
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    @classmethod
    def is_valid_candidate(cls, title: str, content: str) -> bool:
        """
        Return False if content length is < 50 words.
        Return False if title contains blacklisted keywords.
        Return False if title is all uppercase (Spam detection).
        """
        if not title:
            return False
            
        # Check word count (simple split)
        word_count = len(content.split())
        if word_count < 50:
            # print(f"Rejected: Content too short ({word_count} words)")
            return False
            
        # Check blacklist in title
        title_lower = title.lower()
        for keyword in cls.BLACKLIST_KEYWORDS:
            if keyword.lower() in title_lower:
                # print(f"Rejected: Blacklisted keyword '{keyword}' in title")
                return False
                
        # Check spammy title (all caps and long enough to not be an acronym like BTC)
        # Assuming titles shorter than 4 chars could be acronyms/tickers
        if title.isupper() and len(title) > 4:
            # print("Rejected: All uppercase title")
            return False
            
        return True
