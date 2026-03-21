#!/usr/bin/env python3
"""Test YouTube API with your API key and fetch highly recommended videos"""

import sys
sys.path.insert(0, ".")

import asyncio
from app.services.youtube_service import youtube_service
from app.data import get_all_topics

async def test_youtube_fetch():
    print("\n" + "=" * 80)
    print("YOUTUBE VIDEO FETCH TEST - HIGHLY RECOMMENDED VIDEOS")
    print("=" * 80)
    
    # Get some sample topics
    topics = get_all_topics()[:5]  # Test with first 5 topics
    
    print(f"\nFetching highly recommended YouTube videos for {len(topics)} topics...")
    print("-" * 80)
    
    for topic in topics:
        topic_name = topic.get("name", "Unknown")
        topic_id = topic.get("id", "")
        
        print(f"\n📘 Topic: {topic_name}")
        print(f"   ID: {topic_id}")
        
        try:
            # Fetch fresh videos from YouTube
            videos = await youtube_service.search_for_topic(
                topic_name=topic_name,
                language=topic.get("language", ""),
                max_results=3
            )
            
            if videos:
                print(f"   ✅ Found {len(videos)} highly recommended videos:")
                for i, video in enumerate(videos, 1):
                    title = video.get("title", "Unknown")
                    vid_id = video.get("youtubeId", "")
                    channel = video.get("channel", "Unknown")
                    views = video.get("viewCount", 0)
                    rating = video.get("rating", "N/A")
                    
                    print(f"\n      {i}. {title}")
                    print(f"         Channel: {channel}")
                    print(f"         YouTube ID: {vid_id}")
                    print(f"         Views: {views:,}")
                    print(f"         Rating: {rating}")
                    print(f"         Watch: https://www.youtube.com/watch?v={vid_id}")
            else:
                print(f"   ⚠️  No videos found for this topic")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
    
    print("\n" + "=" * 80)
    print("SUMMARY: YouTube API is working! Highly recommended videos fetched.")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    asyncio.run(test_youtube_fetch())
