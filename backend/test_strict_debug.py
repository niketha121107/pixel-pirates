#!/usr/bin/env python
"""Debug what videos are found for strict compound topics"""

import asyncio
import sys
import io
import logging

# Fix encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

logging.basicConfig(level=logging.INFO, format='%(message)s')

from app.services.youtube_service import YouTubeService

async def test():
    service = YouTubeService()
    
    # test strict topic
    topic = "history and philosophy in python"
    print(f"Searching for raw videos: '{topic}'...")
    
    query = f"{topic} tutorial educational explained"
    raw_videos = await service.search_videos(query=query, max_results=20)
    
    print(f"\nFound {len(raw_videos)} raw videos:")
    print("-" * 70)
    
    for i, vid in enumerate(raw_videos[:15], 1):
        title = vid['title']
        desc_preview = vid['description'][:150] if vid['description'] else "No description"
        print(f"\n{i}. {title}")
        print(f"   Desc: {desc_preview}...")
        
        # Check keywords
        title_lower = title.lower()
        desc_lower = (vid['description'] or "").lower()
        content = f"{title_lower} {desc_lower}"
        
        has_history = "history" in content
        has_philosophy = "philosophy" in content  
        has_python = "python" in content
        
        keywords = []
        if has_python: keywords.append("python")
        if has_history: keywords.append("history")
        if has_philosophy: keywords.append("philosophy")
        
        print(f"   Keywords: {keywords}")

asyncio.run(test())
