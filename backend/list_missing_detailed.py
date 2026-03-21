from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["pixel_pirates"]

# Get all topics without videos
missing = list(db.topics.find(
    {"videos": {"$exists": False}},
    {"topicName": 1, "track": 1, "learning_path": 1, "_id": 1}
).sort("track", 1))

print(f"\nFound {len(missing)} topics without videos:\n")
for i, topic in enumerate(missing, 1):
    track = topic.get("track", "N/A")
    name = topic.get("topicName", topic.get("name", "Unknown"))
    print(f"{i:2d}. [{track:20s}] {name}")

print(f"\n{'='*60}")
print(f"Total: {len(missing)} topics need videos")
