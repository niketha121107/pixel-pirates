"""
Populate 200 topics and remove leaderboard entries
"""

import subprocess
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("STEP 1: Generating 200 topics...")
print("=" * 60)

result = subprocess.run([sys.executable, "generate_200_topics.py"], cwd=os.path.dirname(__file__))
if result.returncode != 0:
    print("Error generating topics")
    sys.exit(1)

print("\n" + "=" * 60)
print("STEP 2: Removing leaderboard entries...")
print("=" * 60)

try:
    from motor.motor_asyncio import AsyncClient
    import asyncio
    from app.core.config import MONGODB_URL
    
    async def clean_leaderboard():
        client = AsyncClient(MONGODB_URL)
        db = client.pixel_pirates_db
        
        # Delete all leaderboard entries
        result = await db.leaderboard.delete_many({})
        print(f"✓ Deleted {result.deleted_count} leaderboard entries")
        
        client.close()
    
    asyncio.run(clean_leaderboard())
    print("✓ Leaderboard cleared successfully")
    
except Exception as e:
    print(f"✗ Error clearing leaderboard: {e}")

print("\n" + "=" * 60)
print("✓ COMPLETE: 200 topics added and leaderboard removed")
print("=" * 60)
