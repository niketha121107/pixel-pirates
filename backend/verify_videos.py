from pymongo import MongoClient
import json

db = MongoClient("mongodb://localhost:27017/")["pixel_pirates"]
t = db.topics.find_one()
vids = t.get("recommendedVideos", [])
print(f"Topic: {t.get('name', t.get('topicName'))}")
print(f"Videos: {len(vids)}")
for v in vids:
    print(f"  - {v['youtubeId']}: {v['title']}")

# Count all topics with videos
total = db.topics.count_documents({})
with_videos = db.topics.count_documents({"recommendedVideos": {"$exists": True, "$ne": []}})
print(f"\nTotal topics: {total}")
print(f"Topics with videos: {with_videos}")
