#!/usr/bin/env python
"""Quick test to import vote endpoint and check for errors"""
import sys
import traceback

try:
    from app.models.vote import Vote, VoteOrigin
    print(f"✓ Imported Vote and VoteOrigin: {VoteOrigin.HUMAN}")
    
    from app.api.endpoints.votes import router
    print(f"✓ Imported votes router")
    
    # Try creating Vote instance
    test_vote = Vote(
        user_id=1,
        news_id=1,
        vote_type="trust",
        origin=VoteOrigin.HUMAN
    )
    print(f"✓ Created Vote instance with origin={test_vote.origin}")
    print(f"  origin.value = {test_vote.origin.value}")
    
    print("\n=== All imports successful ===")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    traceback.print_exc()
    sys.exit(1)
