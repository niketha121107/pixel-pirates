from pymongo import MongoClient
from app.core.config import settings

client = MongoClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DATABASE]
topics_collection = db["topics"]

def migrate_youtube_urls():
    topics = list(topics_collection.find({}))
    
    updated_count = 0
    for topic in topics:
        topic_id = topic["_id"]
        updated = False
        
        # We need to check both "recommendedVideos" and "videos" arrays
        for array_name in ["recommendedVideos", "videos"]:
            items = topic.get(array_name, [])
            if not isinstance(items, list):
                continue
                
            for item in items:
                # Use youtubeId or id as the source
                vid = item.get("youtubeId") or item.get("id")
                if vid:
                    item["url"] = f"https://www.youtube.com/watch?v={vid}"
                    updated = True
        
        if updated:
            topics_collection.update_one(
                {"_id": topic_id},
                {"$set": {
                    "recommendedVideos": topic.get("recommendedVideos", []),
                    "videos": topic.get("videos", [])
                }}
            )
            updated_count += 1
            print(f"✅ Updated URLs for topic: {topic.get('topicName', topic_id)}")

    print(f"\n✨ Migration complete! Modified {updated_count} topics.")

if __name__ == "__main__":
    migrate_youtube_urls()