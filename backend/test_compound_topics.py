#!/usr/bin/env python
"""Test compound topic handling"""

import asyncio
from app.services.youtube_service import YouTubeService

async def test_compound_topics():
    service = YouTubeService()
    
    # Test compound topics
    test_topics = [
        "history and philosophy in python",
        "python data structures and algorithms",
        "javascript async programming",
        "python",
        "web development"
    ]
    
    for topic in test_topics:
        print(f"\n{'='*70}")
        print(f"Testing: '{topic}'")
        print(f"{'='*70}")
        
        videos = await service.search_for_topic(topic, "en", max_results=5)
        
        if videos:
            for idx, v in enumerate(videos, 1):
                print(f"\nOK {idx}. {v['title']}")
                print(f"   Channel: {v['channelTitle']}")
                print(f"   Views: {v['viewCount']:,}")
                print(f"   Score: {v['relevanceScore']}")
        else:
            print("NO VIDEOS FOUND")

asyncio.run(test_compound_topics())
