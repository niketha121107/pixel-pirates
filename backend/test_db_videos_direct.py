#!/usr/bin/env python3
"""Direct test of stored videos without API"""

import sys
sys.path.insert(0, ".")

from app.data import get_all_topics, get_mock_data

print("Testing Stored Video Retrieval (Direct DB Access)")
print("=" * 60)

# Initialize data
print("\n1. Loading database...")
get_mock_data()

# Get all topics
print("\n2. Fetching topics...")
topics = get_all_topics()
print(f"   ✅ Retrieved {len(topics)} topics")

# Find a topic with videos
print("\n3. Looking for topics with stored videos...")
topics_with_videos = 0
first_topic_with_video = None

for topic in topics:
    if topic.get("videos"):
        topics_with_videos += 1
        if not first_topic_with_video:
            first_topic_with_video = topic

print(f"   ✅ Found {topics_with_videos} topics with stored videos")

if first_topic_with_video:
    topic_name = first_topic_with_video.get("name", "Unknown")
    videos = first_topic_with_video.get("videos", [])
    
    print(f"\n4. Sample Topic: {topic_name}")
    print(f"   Videos stored: {len(videos)}")
    
    if videos:
        print("\n   Videos Details:")
        for i, video in enumerate(videos[:3], 1):
            print(f"\n   Video {i}:")
            print(f"   - Title: {video.get('title', 'N/A')[:60]}")
            print(f"   - Video ID: {video.get('videoId', 'N/A')}")
            print(f"   - Channel: {video.get('channel', 'N/A')}")
            views = video.get('views', 0)
            print(f"   - Views: {views}")
        
        print("\n   ✅ SUCCESS: Stored videos are available in database!")
    else:
        print("   ⚠️ Topic marked as having videos but list is empty")
else:
    print("   ⚠️ No topics found with stored videos")

print("\n" + "=" * 60)
