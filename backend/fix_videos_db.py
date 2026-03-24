from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["pixel_pirates"]
topics = db["topics"]

videos = [
    {
        "youtubeId": "rfscVS0vtik",
        "title": "Python Full Course",
        "channel": "freeCodeCamp"
    },
    {
        "youtubeId": "8DvywoSXREA",
        "title": "Learn Python",
        "channel": "Tech With Tim"
    },
    {
        "youtubeId": "xF-Ej_gRXfM",
        "title": "JavaScript Tutorial",
        "channel": "Programming with Mosh"
    }
]

count = 0

for topic in topics.find():
    topics.update_one(
        {"_id": topic["_id"]},
        {
            "$set": {
                "recommendedVideos": videos   # ⚠️ IMPORTANT FIELD NAME
            }
        }
    )
    count += 1

print(f"✅ Updated {count} topics with videos")
