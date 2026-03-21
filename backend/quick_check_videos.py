#!/usr/bin/env python
"""Quick check of video population"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check():
    client = AsyncIOMotorClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
    db = client['pixel_pirates']
    
    topics_with_videos = await db.topics.count_documents({'recommendedVideos': {'$exists': True, '$ne': []}})
    total_topics = await db.topics.count_documents({})
    
    print(f'✅ Topics with videos: {topics_with_videos}/{total_topics}')
    if topics_with_videos == total_topics:
        print('✅ ALL TOPICS HAVE VIDEOS!')
    
    # Count total videos
    result = await db.topics.aggregate([
        {'$match': {'recommendedVideos': {'$exists': True}}},
        {'$project': {'count': {'$size': '$recommendedVideos'}}},
        {'$group': {'_id': None, 'total': {'$sum': '$count'}}}
    ]).to_list(None)
    
    if result:
        print(f'✅ Total videos: {result[0]["total"]}')
    
    # Get sample
    sample = await db.topics.find_one({'recommendedVideos': {'$exists': True, '$ne': []}})
    if sample and sample.get('recommendedVideos'):
        print(f"\n📌 Sample topic: {sample.get('name')}")
        videos = sample['recommendedVideos']
        print(f"   Videos count: {len(videos)}")
        for i, v in enumerate(videos[:1], 1):
            print(f"   {i}. {v['youtubeId']} | {v['title'][:50]}")

asyncio.run(check())
