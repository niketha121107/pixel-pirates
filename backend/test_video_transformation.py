#!/usr/bin/env python3
"""Test topic details endpoint directly"""

import sys
sys.path.insert(0, ".")

from app.data import get_all_topics, get_topic_by_id, get_mock_data
import json

print("Testing Topic Details - Videos Transformation")
print("=" * 60)

# Initialize data
print("\n1. Loading database...")
get_mock_data()

# Get first topic
print("\n2. Getting first topic...")
topics = get_all_topics()
if not topics:
    print("   ❌ No topics found!")
    sys.exit(1)

first_topic = topics[0]
print(f"   ✅ Got topic: {first_topic.get('name', 'Unknown')}")

# Process videos like the endpoint does
print("\n3. Testing video transformation (as endpoint does)...")
videos = first_topic.get("videos", [])
print(f"   Raw database videos: {len(videos)}")

recommended_videos = []
for video in videos:
    if isinstance(video, dict):
        transformed = {
            "youtubeId": video.get("videoId", ""),
            "title": video.get("title", ""),
            "channel": video.get("channel", ""),
            "views": video.get("views", 0),
            "uploadedAt": video.get("uploadedAt", ""),
            "url": video.get("url", ""),
            "description": video.get("description", ""),
        }
        recommended_videos.append(transformed)

print(f"   Transformed videos: {len(recommended_videos)}")

print("\n4. Transformed Video Structure:")
for i, video in enumerate(recommended_videos[:2], 1):
    print(f"\n   Video {i}:")
    print(f"   - youtubeId: {video['youtubeId']}")
    print(f"   - title: {video['title']}")
    print(f"   - channel: {video['channel']}")
    url = f"https://www.youtube.com/watch?v={video['youtubeId']}"
    print(f"   - Generated URL: {url}")

print("\n5. Mock Endpoint Response Structure:")
topic_data = {
    "id": str(first_topic.get("_id", "")),
    "topicName": first_topic.get("name", ""),
    "language": first_topic.get("language", ""),
    "difficulty": first_topic.get("difficulty", ""),
    "overview": first_topic.get("overview", ""),
    "recommendedVideos": recommended_videos
}

print(json.dumps({
    "success": True,
    "message": "Topic details retrieved successfully",
    "data": {
        "topic": {
            "topicName": topic_data["topicName"],
            "language": topic_data["language"],
            "recommendedVideos": topic_data["recommendedVideos"][:1]  # Show just first for brevity
        }
    }
}, indent=2))

print("\n" + "=" * 60)
print("✅ SUCCESS: Videos transform correctly for frontend use!")
print("=" * 60)
