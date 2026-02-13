"""
Phase 5: User Reputation System
Weights user votes based on historical accuracy
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict
from app.models.user import User
from app.models.vote import Vote
from app.models.news import News, VerificationStatus
from app.core.logger import log

class UserReputationSystem:
    """
    Calculates and tracks user voting accuracy for weighted consensus
    """
    
    @staticmethod
    async def calculate_user_accuracy(user_id: int, db: AsyncSession) -> Dict[str, float]:
        """
        Calculate user's voting accuracy based on verified outcomes
        
        Returns:
            dict with accuracy_score (0-100), total_votes, correct_votes
        """
        # Get all votes by this user on verified/debunked news
        query = select(Vote, News).join(
            News, Vote.news_id == News.id
        ).where(
            Vote.user_id == user_id,
            News.verification_status.in_([
                VerificationStatus.VERIFIED,
                VerificationStatus.DEBUNKED
            ])
        )
        
        result = await db.execute(query)
        vote_news_pairs = result.all()
        
        if not vote_news_pairs:
            return {
                "accuracy_score": 50.0,  # Neutral starting score
                "total_votes": 0,
                "correct_votes": 0,
                "reputation_tier": "Novice"
            }
        
        total_votes = len(vote_news_pairs)
        correct_votes = 0
        
        for vote, news in vote_news_pairs:
            # "trust" vote is correct if news was VERIFIED
            # "fake" vote is correct if news was DEBUNKED
            if vote.vote_type == "trust" and news.verification_status == VerificationStatus.VERIFIED:
                correct_votes += 1
            elif vote.vote_type == "fake" and news.verification_status == VerificationStatus.DEBUNKED:
                correct_votes += 1
        
        accuracy_score = (correct_votes / total_votes) * 100 if total_votes > 0 else 50.0
        
        # Reputation tiers
        if accuracy_score >= 80 and total_votes >= 50:
            tier = "Expert"
        elif accuracy_score >= 70 and total_votes >= 20:
            tier = "Advanced"
        elif accuracy_score >= 60 and total_votes >= 10:
            tier = "Intermediate"
        else:
            tier = "Novice"
        
        log.info(
            f"User {user_id} accuracy: {accuracy_score:.1f}% "
            f"({correct_votes}/{total_votes}) - Tier: {tier}"
        )
        
        return {
            "accuracy_score": round(accuracy_score, 1),
            "total_votes": total_votes,
            "correct_votes": correct_votes,
            "reputation_tier": tier
        }
    
    @staticmethod
    def get_vote_weight(accuracy_score: float, reputation_tier: str) -> float:
        """
        Calculate vote weight multiplier based on reputation
        
        Returns:
            float between 0.5 (low reputation) and 3.0 (expert)
        """
        # Base weight from accuracy
        if accuracy_score >= 85:
            weight = 3.0
        elif accuracy_score >= 75:
            weight = 2.0
        elif accuracy_score >= 65:
            weight = 1.5
        elif accuracy_score >= 55:
            weight = 1.0
        elif accuracy_score >= 45:
            weight = 0.75
        else:
            weight = 0.5
        
        return weight
    
    @staticmethod
    async def get_weighted_consensus(news_id: int, db: AsyncSession) -> Dict[str, any]:
        """
        Calculate weighted voting consensus for a news item
        
        Returns:
            dict with trust_score, fake_score, consensus, total_weight
        """
        # Get all votes for this news
        query = select(Vote, User).join(
            User, Vote.user_id == User.id
        ).where(Vote.news_id == news_id)
        
        result = await db.execute(query)
        vote_user_pairs = result.all()
        
        if not vote_user_pairs:
            return {
                "trust_score": 0,
                "fake_score": 0,
                "consensus": "UNKNOWN",
                "total_weight": 0,
                "vote_count": 0
            }
        
        trust_weight = 0
        fake_weight = 0
        total_weight = 0
        
        reputation_system = UserReputationSystem()
        
        for vote, user in vote_user_pairs:
            # Calculate user's reputation
            user_stats = await reputation_system.calculate_user_accuracy(user.id, db)
            vote_weight = reputation_system.get_vote_weight(
                user_stats["accuracy_score"],
                user_stats["reputation_tier"]
            )
            
            if vote.vote_type == "trust":
                trust_weight += vote_weight
            elif vote.vote_type == "fake":
                fake_weight += vote_weight
            
            total_weight += vote_weight
        
        # Determine consensus (60% threshold)
        trust_pct = (trust_weight / total_weight * 100) if total_weight > 0 else 0
        fake_pct = (fake_weight / total_weight * 100) if total_weight > 0 else 0
        
        if trust_pct >= 60:
            consensus = "TRUSTED"
        elif fake_pct >= 60:
            consensus = "FAKE"
        else:
            consensus = "DISPUTED"
        
        log.info(
            f"News {news_id} weighted consensus: {consensus} "
            f"(Trust: {trust_pct:.1f}%, Fake: {fake_pct:.1f}%)"
        )
        
        return {
            "trust_score": round(trust_weight, 2),
            "fake_score": round(fake_weight, 2),
            "trust_pct": round(trust_pct, 1),
            "fake_pct": round(fake_pct, 1),
            "consensus": consensus,
            "total_weight": round(total_weight, 2),
            "vote_count": len(vote_user_pairs)
        }
