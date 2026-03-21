#!/usr/bin/env python
"""Quick check of current database status"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import json

async def main():
    print("=" * 80)
    print("CHECKING DATABASE STATUS")
    print("=" * 80)
    
    try:
        client = AsyncIOMotorClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        db = client['pixel_pirates']
        
        # Get collection stats
        collections = await db.list_collection_names()
        print(f"\n✅ Connected to MongoDB")
        print(f"Collections: {collections}")
        
        # Check topics count
        topics_count = await db.topics.count_documents({})
        print(f"\nTopics in database: {topics_count}")
        
        # Check one random topic
        topic = await db.topics.find_one({'recommendedVideos': {'$exists': True, '$ne': []}})
        
        if topic:
            print(f"\n✅ Found topic with videos:")
            print(f"   Name: {topic.get('topicName')}")
            videos = topic.get('recommendedVideos', [])
            print(f"   Videos: {len(videos)}")
            for i, v in enumerate(videos[:2], 1):
                print(f"     - {v.get('youtubeId')}: {v.get('title')[:50]}")
        else:
            print(f"\n❌ No topics with videos found!")
            
            # Check if any topics exist at all
            sample = await db.topics.find_one({})
            if sample:
                print(f"   Found topic: {sample.get('topicName')}")
                print(f"   Structure keys: {list(sample.keys())}")
                videos = sample.get('recommendedVideos', [])
                print(f"   recommendedVideos field: {len(videos)} videos")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(main())
