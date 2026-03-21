#!/usr/bin/env python
"""Database status check - write to file"""
import sys
sys.path.insert(0, ".")

try:
    from pymongo import MongoClient
    from app.core.config import Settings

    settings = Settings()
    client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
    db = client[settings.MONGODB_DATABASE]

    topics_count = db.topics.count_documents({})
    leaderboard_count = db.leaderboard.count_documents({})

    # Delete leaderboard if it has entries
    deleted = 0
    if leaderboard_count > 0:
        result = db.leaderboard.delete_many({})
        deleted = result.deleted_count

    # Write status to file
    with open("_db_status.txt", "w", encoding="utf-8") as f:
        f.write(f"Topics Count: {topics_count}\n")
        f.write(f"Leaderboard Deleted: {deleted}\n")
        status = "SUCCESS - 200 topics added!" if topics_count >= 200 else f"PARTIAL - only {topics_count}/200 topics"
        f.write(f"Status: {status}\n")

    client.close()
    print("Status written to _db_status.txt")

except Exception as e:
    with open("_db_status.txt", "w") as f:
        f.write(f"ERROR: {str(e)}\n")
    print(f"ERROR: {e}")
