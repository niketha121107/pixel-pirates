#!/usr/bin/env python
"""Remove specific topic from database"""

from app.core.database import db, connect_to_mongo
from app.core.config import settings
import asyncio

async def remove_topic():
    """Remove 'history and philosophy in python' topic"""
    try:
        # Connect to database first
        await connect_to_mongo(settings)
        
        if db.database is None:
            print("❌ Failed to connect to database")
            return
        
        topics_collection = db.database["topics"]
        
        # Find and delete all instances of the topic "History & Philosophy"
        # (appears to be duplicated in database)
        result = await topics_collection.delete_many(
            {"topicName": "History & Philosophy"}
        )
        
        if result.deleted_count > 0:
            print(f"✅ Successfully removed topic: 'History & Philosophy'")
            print(f"   Deleted documents: {result.deleted_count}")
        else:
            print("❌ Topic 'History & Philosophy' not found")
            
            # Show available topics for reference
            print("\nAvailable 'History & Philosophy' like topics:")
            cursor = topics_collection.find(
                {"topicName": {"$regex": "history|philosophy", "$options": "i"}}
            )
            topics = await cursor.to_list(length=20)
            for topic in topics:
                print(f"  - {topic.get('topicName')}")
                
    except Exception as e:
        print(f"❌ Error removing topic: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if db.client:
            db.client.close()
            print("✅ Database connection closed")

if __name__ == "__main__":
    asyncio.run(remove_topic())
