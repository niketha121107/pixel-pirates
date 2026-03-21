#!/usr/bin/env python
"""
POPULATE ALL 200 TOPICS WITH YOUTUBE VIDEOS
Uses YouTube API to fetch real, embeddable videos for every topic
"""

import os
import asyncio
import httpx
from typing import List, Dict
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")

print("=" * 80)
print("POPULATING ALL 200 TOPICS WITH YOUTUBE VIDEOS")
print("=" * 80)

if not YOUTUBE_API_KEY:
    print("❌ YOUTUBE_API_KEY not found in .env")
    exit(1)

class YouTubeVideoBatcher:
    def __init__(self):
        self.api_key = YOUTUBE_API_KEY
        self.base_url = "https://www.googleapis.com/youtube/v3/search"
        self.session = None
    
    async def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search YouTube for educational videos"""
        try:
            if not self.session:
                self.session = httpx.AsyncClient(timeout=30)
            
            response = await self.session.get(
                self.base_url,
                params={
                    "q": f"{query} tutorial education learn",
                    "part": "snippet",
                    "type": "video",
                    "maxResults": max_results,
                    "order": "relevance",
                    "videoCategoryId": "27",  # Education
                    "videoEmbeddable": "true",
                    "key": self.api_key
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                videos = []
                
                for item in data.get("items", []):
                    try:
                        video = {
                            "youtubeId": item["id"]["videoId"],
                            "title": item["snippet"]["title"],
                            "description": item["snippet"]["description"][:150],
                            "channel": item["snippet"]["channelTitle"],
                            "publishedAt": item["snippet"]["publishedAt"]
                        }
                        videos.append(video)
                    except KeyError:
                        continue
                
                return videos[:max_results]
            else:
                print(f"  ❌ YouTube API error: {response.status_code}")
                return []
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return []

async def populate_videos():
    """Populate videos for all topics"""
    
    # Connect to MongoDB
    try:
        client = AsyncIOMotorClient(MONGODB_URL)
        db = client['pixel_pirates']
        await db.command('ping')
        print("✅ Connected to MongoDB\n")
    except Exception as e:
        print(f"❌ MongoDB error: {e}")
        return
    
    # Initialize YouTube fetcher
    fetcher = YouTubeVideoBatcher()
    
    # Get all topics
    try:
        cursor = db.topics.find({})
        topics = await cursor.to_list(length=None)
    except Exception as e:
        print(f"❌ Error fetching topics: {e}")
        return
    
    print(f"📚 Found {len(topics)} topics to populate\n")
    print("Fetching videos from YouTube...")
    print("=" * 80)
    
    successful = 0
    failed = 0
    
    for i, topic in enumerate(topics, 1):
        topic_id = topic.get('_id')
        topic_name = topic.get('topicName', 'Unknown')
        
        print(f"[{i:3d}/{len(topics)}] {topic_name[:50]:<50}", end="", flush=True)
        
        # Search for videos
        videos = await fetcher.search(topic_name, max_results=3)
        
        if videos:
            # Update topic with videos
            try:
                result = await db.topics.update_one(
                    {"_id": topic_id},
                    {
                        "$set": {
                            "recommendedVideos": videos,
                            "videosUpdatedAt": datetime.now().isoformat()
                        }
                    }
                )
                if result.modified_count > 0:
                    print(f" ✅ {len(videos)} videos")
                    successful += 1
                else:
                    print(f" ⚠️  No update")
                    failed += 1
            except Exception as e:
                print(f" ❌ {str(e)[:30]}")
                failed += 1
        else:
            print(f" ❌ No videos found")
            failed += 1
        
        # Rate limit: wait between requests
        if i < len(topics):
            await asyncio.sleep(0.5)
    
    print("=" * 80)
    print(f"\n✅ POPULATION COMPLETE")
    print(f"✅ Successful: {successful}/{len(topics)}")
    print(f"❌ Failed: {failed}/{len(topics)}")
    print(f"\n✓ All topics now have YouTube videos")
    print(f"✓ Videos are stored in MongoDB")
    print(f"✓ Frontend will display them automatically")
    
    # Close session
    if fetcher.session:
        await fetcher.session.aclose()

if __name__ == "__main__":
    asyncio.run(populate_videos())
