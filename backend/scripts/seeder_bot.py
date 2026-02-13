"""Seeder Bot - Cold Start Solution with Ethical Data Separation"""
import asyncio
import random
from datetime import datetime, timedelta
from sqlalchemy import select, func
from app.db.session import AsyncSessionLocal
from app.models.news import News
from app.models.user import User
from app.models.vote import Vote, VoteOrigin

# Configuration
BOT_NAMES = [
    "crypto_analyst_bot",
    "defi_watcher_bot",
    "market_observer_bot",
    "blockchain_monitor_bot",
    "token_tracker_bot"
]

SUNSET_DAYS = 14  # Auto-disable after 14 days
MIN_ORGANIC_ACTIVITY = 50  # votes/hour from real users

class SeederBot:
    def __init__(self):
        self.launch_date = datetime(2026, 2, 7)  # Update to actual launch date
        self.bot_users = []
    
    async def create_bot_users(self, db):
        """Create system bot users"""
        for name in BOT_NAMES:
            result = await db.execute(
                select(User).where(User.email == f"{name}@system.coin87")
            )
            bot = result.scalars().first()
            
            if not bot:
                bot = User(
                    email=f"{name}@system.coin87",
                    api_key=f"BOT_{name.upper()}",
                    tier="Free",
                    balance=0.0
                )
                db.add(bot)
        
        await db.commit()
        
        # Fetch all bots
        result = await db.execute(
            select(User).where(User.email.like("%@system.coin87"))
        )
        self.bot_users = result.scalars().all()
        print(f"✓ {len(self.bot_users)} bot users ready")
    
    async def check_sunset(self) -> bool:
        """Check if bot should be disabled"""
        days_since_launch = (datetime.utcnow() - self.launch_date).days
        
        if days_since_launch > SUNSET_DAYS:
            print(f"⏰ Sunset triggered: {days_since_launch} days since launch")
            return True
        
        return False
    
    async def check_organic_activity(self, db) -> bool:
        """Check if organic activity is sufficient"""
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        result = await db.execute(
            select(func.count(Vote.id))
            .where(Vote.origin == VoteOrigin.HUMAN)
            .where(Vote.created_at >= one_hour_ago)
        )
        organic_votes = result.scalar()
        
        if organic_votes > MIN_ORGANIC_ACTIVITY:
            print(f"✓ Organic activity sufficient: {organic_votes} votes/hour")
            return True
        
        return False
    
    async def seed_votes(self, db):
        """Add bot votes to recent news"""
        # Get recent news with 0 or low votes (last 2 hours)
        two_hours_ago = datetime.utcnow() - timedelta(hours=2)
        
        result = await db.execute(
            select(News)
            .where(News.created_at >= two_hours_ago)
            .order_by(News.created_at.desc())
            .limit(10)
        )
        recent_news = result.scalars().all()
        
        if not recent_news:
            print("No recent news to seed")
            return
        
        votes_added = 0
        
        for news in recent_news:
            # Check existing vote count
            result = await db.execute(
                select(func.count(Vote.id)).where(Vote.news_id == news.id)
            )
            existing_votes = result.scalar()
            
            if existing_votes > 5:
                continue  # Already has activity
            
            # Bot decision based on AI confidence
            if news.confidence_score and news.confidence_score > 0.8:
                # High confidence - bots vote based on sentiment
                num_bots = random.randint(2, 4)
                
                for _ in range(num_bots):
                    bot = random.choice(self.bot_users)
                    
                    # Check if bot already voted
                    result = await db.execute(
                        select(Vote).where(
                            Vote.user_id == bot.id,
                            Vote.news_id == news.id
                        )
                    )
                    if result.scalars().first():
                        continue
                    
                    # Vote based on sentiment
                    vote_type = "trust" if news.sentiment_label == "Bullish" else "fake"
                    
                    vote = Vote(
                        user_id=bot.id,
                        news_id=news.id,
                        vote_type=vote_type,
                        origin=VoteOrigin.SYSTEM_BOT  # CRITICAL: Mark as bot
                    )
                    db.add(vote)
                    votes_added += 1
                    
                    # Random delay simulation
                    await asyncio.sleep(random.uniform(0.5, 2.0))
        
        await db.commit()
        print(f"✓ Added {votes_added} bot votes")
    
    async def run(self):
        """Main seeder loop"""
        async with AsyncSessionLocal() as db:
            # Create bots if not exist
            await self.create_bot_users(db)
            
            # Check sunset conditions
            if await self.check_sunset():
                print("🌅 Seeder bot sunset - stopping permanently")
                return
            
            if await self.check_organic_activity(db):
                print("✓ Organic activity detected - bots yielding to humans")
                return
            
            # Seed votes
            await self.seed_votes(db)

if __name__ == "__main__":
    bot = SeederBot()
    asyncio.run(bot.run())
