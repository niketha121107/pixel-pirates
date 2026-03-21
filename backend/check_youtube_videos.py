#!/usr/bin/env python
"""Verify YouTube videos are available and playable in the database"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check_videos():
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    db = client['pixel_pirates']
    
    print("=" * 80)
    print("CHECKING YOUTUBE VIDEOS IN DATABASE")
    print("=" * 80)
    
    # Get first 5 topics
    cursor = db.topics.find({}).limit(5)
    topics = await cursor.to_list(length=5)
    
    print(f"\n📊 Checking {len(topics)} topics for videos...\n")
    
    for i, topic in enumerate(topics, 1):
        topic_name = topic.get('topicName', 'Unknown')
        videos = topic.get('recommendedVideos', [])
        
        print(f"{i}. {topic_name}")
        print(f"   Videos: {len(videos)} found")
        
        if videos:
            for j, video in enumerate(videos, 1):
                youtube_id = video.get('youtubeId', 'MISSING')
                title = video.get('title', 'No title')[:60]
                
                # Validate YouTube ID format
                is_valid = len(youtube_id) == 11 and youtube_id != 'MISSING'
                status = "✅" if is_valid else "❌"
                
                print(f"     {j}. {status} ID: {youtube_id}")
                print(f"        Title: {title}")
                
                # Generate playable URL
                if is_valid:
                    url = f"https://www.youtube.com/embed/{youtube_id}"
                    print(f"        URL: {url}")
        else:
            print(f"   ❌ No videos found!")
        
        print()
    
    # Get statistics
    all_topics = await db.topics.count_documents({})
    topics_with_videos = await db.topics.count_documents({"recommendedVideos": {"$exists": True, "$ne": []}})
    
    print("=" * 80)
    print("STATISTICS")
    print("=" * 80)
    print(f"Total topics: {all_topics}")
    print(f"Topics with videos: {topics_with_videos}")
    print(f"Coverage: {(topics_with_videos/all_topics*100):.1f}%")

if __name__ == "__main__":
    asyncio.run(check_videos())
