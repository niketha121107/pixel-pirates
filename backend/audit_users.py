import pymongo
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['pixel_pirates']

for u in db.users.find():
    completed = u.get("completedTopics", [])
    pending = u.get("pendingTopics", [])
    in_progress = u.get("inProgressTopics", [])
    total = len(completed) + len(pending) + len(in_progress)
    hours = u.get("totalHours", 0)
    print(f"User: {u.get('email', u.get('id', 'N/A'))}")
    print(f"  Total: {total} (C:{len(completed)}, P:{len(pending)}, I:{len(in_progress)})")
    print(f"  Hours: {hours}")
    print("-" * 20)
