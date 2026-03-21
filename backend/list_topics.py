#!/usr/bin/env python
"""Find and list all topics"""

from app.core.database import db, connect_to_mongo
from app.core.config import settings
import asyncio

async def list_all_topics():
    """List all available topics"""
    try:
        await connect_to_mongo(settings)
        
        if db.database is None:
            print("❌ Failed to connect to database")
            return
        
        topics_collection = db.database["topics"]
        
        # Get all topics
        cursor = topics_collection.find({})
        topics = await cursor.to_list(length=None)
        
        print(f"Total topics: {len(topics)}\n")
        print("Topics containing 'history', 'philosophy', or 'python':")
        print("-" * 70)
        
        for topic in topics:
            topic_name = topic.get('topicName', 'N/A')
            if any(word in topic_name.lower() for word in ['history', 'philosophy', 'python']):
                print(f"  - {topic_name}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if db.client:
            db.client.close()

if __name__ == "__main__":
    asyncio.run(list_all_topics())
