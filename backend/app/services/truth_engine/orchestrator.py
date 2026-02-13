"""
Phase 5: Truth Engine Orchestrator
Coordinates all verification services
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.news import News, CategoryType, VerificationStatus
from app.services.truth_engine.tier1_verifier import Tier1Verifier
from app.services.truth_engine.market_verifier import MarketVerifier
from app.services.truth_engine.user_reputation import UserReputationSystem
from app.core.logger import log
from typing import Dict, Any

class TruthEngine:
    """
    Main orchestrator for news verification pipeline
    """
    
    def __init__(self):
        self.tier1_verifier = Tier1Verifier()
        self.market_verifier = MarketVerifier()
        self.reputation_system = UserReputationSystem()
    
    async def verify_news(self, news: News, db: AsyncSession) -> Dict[str, Any]:
        """
        Run complete verification pipeline on a news item
        
        Returns:
            verification_report with status, evidence, and recommendations
        """
        report = {
            "news_id": news.id,
            "title": news.title,
            "initial_status": news.verification_status.value if news.verification_status else "pending",
            "checks_performed": [],
            "evidence": {},
            "final_status": None,
            "confidence_score": 0
        }
        
        confidence_points = 0
        max_points = 0
        
        # Check 1: Tier 1 Source Verification
        log.info(f"Running Tier 1 verification for news {news.id}")
        tier1_verified, tier1_evidence = await self.tier1_verifier.verify_tier1_consensus(news, db)
        
        report["checks_performed"].append("tier1_source_check")
        report["evidence"]["tier1"] = {
            "verified": tier1_verified,
            "evidence": tier1_evidence
        }
        
        if tier1_verified:
            confidence_points += 40
        max_points += 40
        
        # Check 2: Market Data Verification (only for MARKET_MOVE)
        if news.category_type == CategoryType.MARKET_MOVE and news.coins_mentioned:
            log.info(f"Running market data verification for news {news.id}")
            
            # Get primary coin
            primary_coin = news.coins_mentioned[0] if isinstance(news.coins_mentioned, list) else None
            
            if primary_coin:
                market_result = await self.market_verifier.check_market_reality(
                    symbol=primary_coin,
                    publish_time=news.published_at,
                    sentiment=news.sentiment_label or "Neutral",
                    category_type=news.category_type.value if news.category_type else "opinion"
                )
                
                report["checks_performed"].append("market_data_check")
                report["evidence"]["market"] = market_result
                
                if market_result["verification_result"] == "VERIFIED":
                    confidence_points += 30
                elif market_result["verification_result"] == "DEBUNKED":
                    confidence_points -= 50  # Strong negative signal
                
                max_points += 30
        
        # Check 3: User Consensus (if votes exist)
        log.info(f"Checking user consensus for news {news.id}")
        user_consensus = await self.reputation_system.get_weighted_consensus(news.id, db)
        
        report["checks_performed"].append("user_consensus_check")
        report["evidence"]["user_consensus"] = user_consensus
        
        if user_consensus["vote_count"] >= 5:  # Minimum 5 votes
            if user_consensus["consensus"] == "TRUSTED":
                confidence_points += 20
            elif user_consensus["consensus"] == "FAKE":
                confidence_points -= 40
            
            max_points += 20
        
        # Calculate final confidence score (0-100)
        if max_points > 0:
            confidence_score = max(0, min(100, (confidence_points / max_points) * 100 + 50))
        else:
            confidence_score = 50  # Neutral if no checks applicable
        
        report["confidence_score"] = round(confidence_score, 1)
        
        # Determine final verification status
        if confidence_score >= 75:
            final_status = VerificationStatus.VERIFIED
        elif confidence_score <= 30:
            final_status = VerificationStatus.DEBUNKED
        elif confidence_score <= 40 or user_consensus.get("consensus") == "FAKE":
            final_status = VerificationStatus.FLAGGED
        else:
            final_status = VerificationStatus.PENDING
        
        report["final_status"] = final_status.value
        
        # Update news in database
        news.verification_status = final_status
        news.evidence_data = report["evidence"]
        await db.commit()
        
        log.info(
            f"Verification complete for news {news.id}: "
            f"{final_status.value} (confidence: {confidence_score}%)"
        )
        
        return report
