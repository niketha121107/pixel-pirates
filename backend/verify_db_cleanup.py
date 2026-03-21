#!/usr/bin/env python
"""Verify 200 topics and clear leaderboard"""
import sys
sys.path.insert(0, '.')

from pymongo import MongoClient
from app.core.config import Settings

try:
    settings = Settings()
    client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
    db = client[settings.MONGODB_DATABASE]
    
    # Test connection
    client.server_info()
    print("✓ Connected to MongoDB")
    
    # Delete leaderboard
    result = db.leaderboard.delete_many({})
    print(f"✓ Leaderboard: deleted {result.deleted_count} entries")
    
    # Check topics count
    topics_count = db.topics.count_documents({})
    print(f"✓ Topics database: {topics_count} topics loaded")
    
    if topics_count >= 200:
        print("\n✅ SUCCESS: 200 topics added and leaderboard removed!")
    else:
        print(f"\n⚠️  WARNING: Only {topics_count} topics found (expected 200)")
    
    client.close()
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
