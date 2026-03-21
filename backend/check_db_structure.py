#!/usr/bin/env python
"""Check database field names for videos"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import json

async def main():
    print("=" * 80)
    print("CHECKING DATABASE STRUCTURE")
    print("=" * 80)
    
    try:
        client = AsyncIOMotorClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        db = client['pixel_pirates']
        
        # Get a sample topic
        topic = await db.topics.find_one({})
        
        if topic:
            print(f"\n✅ Sample Topic Structure:")
            print(f"   All keys: {list(topic.keys())}")
            
            # Check for video-related fields
            for key in topic.keys():
                if 'video' in key.lower() or 'recommended' in key.lower():
                    value = topic[key]
                    if isinstance(value, list):
                        print(f"\n   🎥 {key}: List with {len(value)} items")
                        if value:
                            print(f"      First item keys: {list(value[0].keys()) if isinstance(value[0], dict) else type(value[0])}")
                    else:
                        print(f"\n   📄 {key}: {type(value).__name__}")
            
            # Check specifically for these fields
            fields_to_check = ['videos', 'recommendedVideos', 'video', 'youtube_videos']
            print(f"\n   Checking specific fields:")
            for field in fields_to_check:
                if field in topic:
                    val = topic[field]
                    if isinstance(val, list):
                        print(f"      ✅ {field}: {len(val)} items")
                        if val:
                            print(f"         Sample: {val[0]}")
                else:
                    print(f"      ❌ {field}: NOT FOUND")
                    
        else:
            print("❌ No topics found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(main())
