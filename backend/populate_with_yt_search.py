import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from youtubesearchpython import VideosSearch

async def main():
    print("=" * 80)
    print("POPULATING YOUTUBE VIDEOS VIA yt-search (NO QUOTA LIMIT)")
    print("=" * 80)
    
    client = AsyncIOMotorClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
    db = client['pixel_pirates']
    
    # Update topics that still have the broken fallback video
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
            # Native scrape (no API key required)
            query = f"{topic_name} {topic.get('language', '')} tutorial programming exact"
            videosSearch = VideosSearch(query, limit=3)
            results = videosSearch.result()
            
            videos = []
            for item in results.get('result', []):
                videos.append({
                    "youtubeId": item.get('id'),
                    "title": item.get('title'),
                    "channel": item.get('channel', {}).get('name', ''),
                    "duration": item.get('duration'),
                    "views": item.get('viewCount', {}).get('short', ''),
                    "description": item.get('descriptionSnippet', [{}])[0].get('text', '') if item.get('descriptionSnippet') else ''
                })
            
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
            
    print(f"\n✅ RECOVERED {updated_count}/{len(topics_list)} topics using YouTube Scraper!")

if __name__ == "__main__":
    asyncio.run(main())
