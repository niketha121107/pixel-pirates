"""
Add full YouTube URL to every video in every topic's recommendedVideos array.
Converts youtubeId → url: https://www.youtube.com/watch?v={youtubeId}
"""
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["pixel_pirates"]
topics = db["topics"]

count = 0
video_count = 0

for topic in topics.find():
    videos = topic.get("recommendedVideos", [])
    updated = False

    for video in videos:
        if video.get("youtubeId") and not video.get("url"):
            video["url"] = f"https://www.youtube.com/watch?v={video['youtubeId']}"
            updated = True
            video_count += 1
        elif video.get("youtubeId") and video.get("url") == "":
            video["url"] = f"https://www.youtube.com/watch?v={video['youtubeId']}"
            updated = True
            video_count += 1

    if updated:
        topics.update_one(
            {"_id": topic["_id"]},
            {"$set": {"recommendedVideos": videos}}
        )
        count += 1

# Verify
sample = topics.find_one({"recommendedVideos": {"$exists": True, "$ne": []}})
print(f"✅ Updated {count} topics, {video_count} videos with URLs")
print(f"\n📋 Sample verification:")
print(f"   Topic: {sample.get('name', sample.get('topicName'))}")
for i, v in enumerate(sample.get("recommendedVideos", []), 1):
    print(f"   {i}. ID: {v.get('youtubeId')}")
    print(f"      URL: {v.get('url')}")
    print(f"      Title: {v.get('title')}")
