#!/usr/bin/env python
"""
Generate and populate real YouTube videos for all topics
Uses YouTube search to find actual videos for each topic
"""

import asyncio
import json
import os
from motor.motor_asyncio import AsyncIOMotorClient
import requests
from datetime import datetime

# Get YouTube API key
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "AIzaSyDMvWFIW-0rFcsX0qyEZH_3R0aF5UZaMuU")

def search_youtube_videos(topic: str, language: str = "Python") -> list:
    """Search YouTube for videos related to a topic"""
    try:
        search_query = f"{topic} {language} tutorial"
        
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "q": search_query,
            "type": "video",
            "part": "snippet",
            "maxResults": 3,
            "order": "relevance",
            "key": YOUTUBE_API_KEY,
            "regionCode": "US"
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 403:
            print(f"⚠️ YouTube API quota exceeded - using fallback videos")
            return get_fallback_videos(topic)
        
        if response.status_code != 200:
            print(f"⚠️ YouTube API error {response.status_code}")
            return get_fallback_videos(topic)
        
        data = response.json()
        videos = []
        
        for item in data.get('items', []):
            try:
                video_id = item['id'].get('videoId', '')
                title = item['snippet'].get('title', '')
                channel = item['snippet'].get('channelTitle', '')
                description = item['snippet'].get('description', '')
                
                if video_id and len(video_id) == 11:
                    videos.append({
                        'youtubeId': video_id,
                        'title': title,
                        'channel': channel,
                        'description': description[:200]
                    })
            except:
                continue
        
        return videos[:3] if videos else get_fallback_videos(topic)
        
    except requests.exceptions.Timeout:
        print(f"⚠️ YouTube API timeout - using fallback")
        return get_fallback_videos(topic)
    except Exception as e:
        print(f"⚠️ YouTube search error: {str(e)[:50]}")
        return get_fallback_videos(topic)


def get_fallback_videos(topic: str) -> list:
    """Fallback: return curated educational videos"""
    fallback_db = {
        'python': [
            {'youtubeId': 'rfscVS0vtik', 'title': 'Python for Everybody', 'channel': 'freeCodeCamp', 'description': 'Complete Python course'},
            {'youtubeId': 'pkZZUhM_x44', 'title': 'Python Full Course', 'channel': 'Programming with Mosh', 'description': 'Learn Python basics'},
            {'youtubeId': '8DvywoSXREA', 'title': 'Learn Python', 'channel': 'Tech with Tim', 'description': 'Python tutorial for beginners'},
        ],
        'javascript': [
            {'youtubeId': 'xF-Ej_gRXfM', 'title': 'JavaScript Tutorial', 'channel': 'Code with Ania Kubow', 'description': 'JavaScript for beginners'},
            {'youtubeId': 'W6NZfCO5tbc', 'title': 'JavaScript Course', 'channel': 'freeCodeCamp', 'description': 'Complete JavaScript tutorial'},
            {'youtubeId': 'PkZYUhM_x44', 'title': 'JavaScript Fundamentals', 'channel': 'Traversy Media', 'description': 'Learn JavaScript'},
        ],
        'html': [
            {'youtubeId': 'PlxWf493en0', 'title': 'HTML and CSS', 'channel': 'freeCodeCamp', 'description': 'HTML and CSS tutorial'},
            {'youtubeId': 'kUMe1FH4CHE', 'title': 'Web Development', 'channel': 'Traversy Media', 'description': 'HTML, CSS, and JavaScript'},
            {'youtubeId': 'w7ejDZ8SWv8', 'title': 'HTML Tutorial', 'channel': 'Scrimba', 'description': 'Learn HTML basics'},
        ],
        'sql': [
            {'youtubeId': 'HXV3zeQKqGY', 'title': 'SQL Tutorial', 'channel': 'Maven Analytics', 'description': 'SQL for data analysis'},
            {'youtubeId': 'OqjAXAN8GUg', 'title': 'MongoDB Tutorial', 'channel': 'freeCodeCamp', 'description': 'NoSQL database tutorial'},
            {'youtubeId': '3O9nYIkOkf0', 'title': 'Databases', 'channel': 'CS50', 'description': 'CS50 database course'},
        ]
    }
    
    # Find best match
    topic_lower = topic.lower()
    for key, videos in fallback_db.items():
        if key in topic_lower:
            return videos
    
    # Return default Python videos if no match
    return fallback_db['python']


async def main():
    print("=" * 80)
    print("POPULATING YOUTUBE VIDEOS FOR ALL TOPICS")
    print("=" * 80)
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        db = client['pixel_pirates']
        
        print("✅ Connected to MongoDB")
        
        # Get all topics
        topics = await db.topics.find({}).to_list(None)
        print(f"📚 Found {len(topics)} topics\n")
        
        updated_count = 0
        
        for i, topic in enumerate(topics, 1):
            topic_name = topic.get('name', 'Unknown')
            language = topic.get('language', 'Python')
            topic_id = topic.get('_id')
            
            print(f"[{i:3d}/{len(topics)}] {topic_name:30s}...", end=" ", flush=True)
            
            try:
                # Search for videos
                videos = search_youtube_videos(topic_name, language)
                
                if videos:
                    # Update MongoDB with both field names for compatibility
                    await db.topics.update_one(
                        {'_id': topic_id},
                        {
                            '$set': {
                                'recommendedVideos': videos,
                                'videos': videos,
                                'videosPopulatedAt': datetime.now().isoformat()
                            }
                        }
                    )
                    print(f"✅ {len(videos)} videos")
                    updated_count += 1
                else:
                    print(f"⚠️ No videos")
                
            except Exception as e:
                print(f"❌ Error")
            
            # Rate limiting for YouTube API
            await asyncio.sleep(0.2)
        
        print("\n" + "=" * 80)
        print(f"✅ POPULATION COMPLETE")
        print("=" * 80)
        print(f"✅ Updated: {updated_count}/{len(topics)} topics")
        
        # Verify
        topics_with_videos = await db.topics.count_documents({'recommendedVideos': {'$exists': True, '$ne': []}})
        total_videos = await db.topics.aggregate([
            {'$match': {'recommendedVideos': {'$exists': True}}},
            {'$project': {'count': {'$size': '$recommendedVideos'}}},
            {'$group': {'_id': None, 'total': {'$sum': '$count'}}}
        ]).to_list(None)
        
        video_count = total_videos[0]['total'] if total_videos else 0
        
        print(f"\n✅ Topics with videos: {topics_with_videos}/200")
        print(f"✅ Total videos: {video_count}")
        print(f"✅ Average per topic: {video_count/max(topics_with_videos, 1):.1f}")
        
        # Sample check
        print(f"\n📋 Sample verification:")
        sample = await db.topics.find_one({'recommendedVideos': {'$exists': True, '$ne': []}})
        if sample and sample.get('recommendedVideos'):
            print(f"   Topic: {sample.get('name')}")
            for i, v in enumerate(sample['recommendedVideos'][:2], 1):
                print(f"   {i}. {v['youtubeId']} | {v['title'][:40]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
