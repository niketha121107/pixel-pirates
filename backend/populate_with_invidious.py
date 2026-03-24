import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.services.youtube_service import youtube_service

async def main():
    print("=" * 80)
    print("POPULATING YOUTUBE VIDEOS VIA INVIDIOUS (QUOTA BYPASS)")
    print("=" * 80)
    
    client = AsyncIOMotorClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
    db = client['pixel_pirates']
    
    # Only update topics that have the broken fallback video
    topics = await db.topics.find({'videos.youtubeId': 'rfscVS0vtik'}).to_list(None)
    
    # Also find topics with NO videos just in case
    no_video_topics = await db.topics.find({'videos': {'$exists': False}}).to_list(None)
    empty_video_topics = await db.topics.find({'videos': {'$size': 0}}).to_list(None)
    
    all_topics_to_fix = {t['_id']: t for t in topics + no_video_topics + empty_video_topics}.values()
    topics_list = list(all_topics_to_fix)
    
    print(f"📚 Found {len(topics_list)} topics needing video generation\n")
    
    updated_count = 0
    for i, topic in enumerate(topics_list, 1):
        topic_name = topic.get('name', 'Unknown')
        topic_id = topic.get('_id')
        print(f"[{i:3d}/{len(topics_list)}] {topic_name:30s}...", end=" ", flush=True)
        
        try:
            # Using Invidious to search
            videos = await youtube_service.search_via_invidious(topic_name, max_results=3)
            if videos:
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
                print(f"⚠️ No videos found")
        except Exception as e:
            print(f"❌ Error: {e}")
            
    print(f"\n✅ RECOVERED {updated_count}/{len(topics_list)} topics using Invidious!")

if __name__ == "__main__":
    asyncio.run(main())
