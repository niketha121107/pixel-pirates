#!/usr/bin/env python3
"""Quick test to check YouTube service directly"""

import sys
import os
import asyncio
import logging
sys.path.insert(0, ".")

# Enable detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s - %(levelname)s - %(message)s'
)

from app.services.youtube_service import youtube_service

async def test_youtube():
    topic_name = "Python Async Programming"

    print(f"\nTesting YouTube Service for: {topic_name}")
    print("=" * 60)

    # Test search
    videos = await youtube_service.search_for_topic(
        topic_name=topic_name,
        language="en",
        max_results=3
    )

    print(f"\nSearch completed")
    print(f"Videos found: {len(videos)}")

    if videos:
        for i, video in enumerate(videos[:3], 1):
            print(f"\n  Video {i}:")
            print(f"    Title: {video.get('title', 'N/A')[:70]}")
            print(f"    YouTube ID: {video.get('youtubeId', 'N/A')}")
            print(f"    Channel: {video.get('channelTitle', 'N/A')}")
            print(f"    Views: {video.get('viewCount', 0):,}")
            print(f"    Source: {video.get('source', 'unknown')}")
    else:
        print("   No videos found!")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_youtube())
