#!/usr/bin/env python
"""Check topic IDs in database"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    print("Getting topic IDs from database...")
    
    try:
        client = AsyncIOMotorClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        db = client['pixel_pirates']
        
        # Get first 5 topics
        topics = await db.topics.find({}).limit(5).to_list(None)
        
        print(f"\nFirst 5 topics:")
        for i, topic in enumerate(topics, 1):
            topic_id = topic.get('id') or str(topic.get('_id', ''))
            topic_name = topic.get('name', 'Unknown')
            print(f"  {i}. ID: {topic_id} | Name: {topic_name}")
        
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(main())
