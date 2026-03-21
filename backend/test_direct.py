#!/usr/bin/env python
"""Direct test of search_for_topic"""

import asyncio
import sys
import io
import logging

# Fix encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s')

from app.services.youtube_service import YouTubeService

async def test():
    service = YouTubeService()
    
    print("Testing 'history and philosophy in python'...")
    result = await service.search_for_topic("history and philosophy in python", "en", max_results=5)
    print(f"Result count: {len(result)}")
    for i, vid in enumerate(result, 1):
        print(f"  {i}. {vid['title']} ({vid['viewCount']:,} views)")

asyncio.run(test())
