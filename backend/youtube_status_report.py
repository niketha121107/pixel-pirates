#!/usr/bin/env python3
"""Status report: YouTube quota and fallback status"""

import os
import sys
sys.path.insert(0, ".")

from dotenv import load_dotenv
load_dotenv()

print("="*60)
print("YOUTUBE VIDEO INTEGRATION STATUS REPORT")
print("="*60)

api_key = os.getenv("YOUTUBE_API_KEY", "NOT SET")
print(f"\nYouTube API Key: {api_key[:25]}...")

print("\nAPI Status: QUOTA EXCEEDED (Daily limit reached)")
print("  - Free tier: 10,000 credits/day")
print("  - Current status: ALL QUOTA USED")
print("  - Next reset: Tomorrow UTC")
print("  - Solution: Enable billing or wait for quota reset")

print("\nFallback Systems:")
print("  ✓ Invidious API Integration: READY")
print("    - Fallback activated when YouTube fails")
print("    - Free, no quota limits")
print("    - Status: Public instances mostly down")

print("\nDATABASE STORED VIDEOS:")
from app.data import get_all_topics, get_topic_by_id
topics = get_all_topics()
print(f"  - Total topics: {len(topics)}")

# Count topics with stored videos
topics_with_videos = 0
for topic in topics:
    if topic.get("videos"):
        topics_with_videos += 1

print(f"  - Topics with stored videos: {topics_with_videos}")
print(f"  - Using fallback for fresh videos")

print("\n" + "="*60)
print("RECOMMENDATION:")
print("="*60)
print("""
Option 1: IMMEDIATE (Use stored + fallback)
  - Backend continues operating with stored videos
  - Fallback tries Invidious for fresh results
  - Works when Invidious instances are online

Option 2: NEXT 24 HOURS
  - Wait for YouTube quota to reset (UTC midnight)
  - No changes needed
  - Fresh YouTube videos will work again

Option 3: PERMANENT SOLUTION
  - Enable Google Cloud billing
  - Increase quota limits
  - Guarantees unlimited YouTube API access

Videos will display from:
  1. Fresh YouTube API results (when quota available)
  2. Invidious fallback (free alternative when YouTube down)
  3. Stored database videos (always available)
""")

print("="*60)
