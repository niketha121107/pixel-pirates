#!/usr/bin/env python
"""Test YouTube API with strict topic-specific filtering"""

import asyncio
from app.services.youtube_service import YouTubeService

async def test_youtube_filtering():
    service = YouTubeService()
    
    # Test topics
    test_topics = [
        "Python",
        "JavaScript loops",
        "Data Structures",
        "REST API"
    ]
    
    for topic in test_topics:
        print(f"\n{'='*60}")
        print(f"Testing: {topic}")
        print(f"{'='*60}")
        
        videos = await service.search_for_topic(topic, "en", max_results=1)
        
        if videos:
            for idx, v in enumerate(videos, 1):
                print(f"\n{idx}. {v['title']}")
                print(f"   Channel: {v['channelTitle']}")
                print(f"   Views: {v['viewCount']:,}")
                print(f"   Score: {v['relevanceScore']}")
                print(f"   URL: https://youtube.com/watch?v={v['youtubeId']}")
        else:
            print("❌ No videos found (filtering was VERY strict)")

asyncio.run(test_youtube_filtering())
