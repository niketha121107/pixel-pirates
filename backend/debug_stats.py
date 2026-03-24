import pymongo
from bson import ObjectId

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['pixel_pirates']
user = db.users.find_one()

if user:
    completed = user.get("completedTopics", [])
    pending = user.get("pendingTopics", [])
    in_progress = user.get("inProgressTopics", [])
    total_hours = user.get("totalHours", 0)
    
    all_ids = completed + pending + in_progress
    unique_ids = set(all_ids)
    
    print(f"User ID: {user['_id']}")
    print(f"Completed ({len(completed)})")
    print(f"Pending ({len(pending)})")
    print(f"In Progress ({len(in_progress)})")
    print(f"Total Unique: {len(unique_ids)}")
    print(f"Total Sum: {len(completed) + len(pending) + len(in_progress)}")
    print(f"Total Hours Raw: {total_hours}")
    
    # Check if all IDs in lists actually exist in topics collection
    # Note: the topic IDs are stored as strings in the user object
    topic_ids = set(str(doc["_id"]) for doc in db.topics.find({}, {"_id": 1}))
    missing_ids = unique_ids - topic_ids
    print(f"Missing IDs (in progress but not in topics): {len(missing_ids)}")
    if missing_ids:
        print(f"Example Missing: {list(missing_ids)[:3]}")
    
    # Check topics count
    print(f"Total topics in DB: {len(topic_ids)}")
else:
    print("No user found")
