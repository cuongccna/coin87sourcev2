import re
from typing import List, Tuple
from app.core.taxonomy import COIN_KEYWORDS, TOPIC_KEYWORDS

class KeywordTagger:
    @staticmethod
    def extract_tags(text: str) -> Tuple[List[str], str]:
        """
        Scans text (title + content) against the taxonomy.
        Returns:
            - List of found coins (e.g., ['BTC', 'ETH'])
            - Primary Topic Category (e.g., 'DeFi') - currently returns the first matched or None
        """
        if not text:
            return [], None
        
        text_lower = text.lower()
        found_coins = set()
        found_topics = set()
        
        # Check Coins
        for coin, keywords in COIN_KEYWORDS.items():
            for kw in keywords:
                # Use regex boundry to avoid partial match (e.g. 'sol' in 'absolute')
                # Simple check first for speed, then regex if strictly needed. 
                # For now, simple containment or word boundry regex.
                if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                    found_coins.add(coin)
                    break 
        
        # Check Topics
        for topic, keywords in TOPIC_KEYWORDS.items():
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                    found_topics.add(topic)
                    break
        
        # Determine primary topic (primitive logic: just take the first one found)
        primary_topic = list(found_topics)[0] if found_topics else None
        
        return list(found_coins), primary_topic

    @staticmethod
    def is_relevant(text: str) -> bool:
        """
        Returns True if ANY crypto-related keyword (Coin or Topic) is found.
        Also checks against a general 'crypto' whitelist if needed.
        """
        coins, topic = KeywordTagger.extract_tags(text)
        if coins or topic:
            return True
            
        # Optional: Add general crypto terms if no specific coin/topic found
        general_terms = ['crypto', 'blockchain', 'web3', 'wallet', 'exchange', 'token']
        text_lower = text.lower()
        for term in general_terms:
             if re.search(r'\b' + re.escape(term) + r'\b', text_lower):
                 return True
                 
        return False
