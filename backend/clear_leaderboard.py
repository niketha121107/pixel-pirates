"""
Clear leaderboard entries from MongoDB
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from pymongo import MongoClient
    from app.core.config import Settings
    
    settings = Settings()
    client = MongoClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DATABASE]
    result = db.leaderboard.delete_many({})
    print(f"✓ Deleted {result.deleted_count} leaderboard entries")
    client.close()
    print("✓ Leaderboard cleared successfully")
    
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
