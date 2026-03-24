import pymongo
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['pixel_pirates']

for u in db.users.find():
    completed = set(u.get("completedTopics", []))
    pending = set(u.get("pendingTopics", []))
    in_progress = set(u.get("inProgressTopics", []))
    
    overlap_cp = completed & pending
    overlap_ci = completed & in_progress
    overlap_ip = in_progress & pending
    
    total = len(completed) + len(pending) + len(in_progress)
    hours = u.get("totalHours", 0)
    
    print(f"User: {u.get('email', u.get('id', 'N/A'))}")
    print(f"  Total: {total}")
    if overlap_cp or overlap_ci or overlap_ip:
        print(f"  OVERLAP FOUND!")
        if overlap_cp: print(f"    C-P overlap: {list(overlap_cp)}")
        if overlap_ci: print(f"    C-I overlap: {list(overlap_ci)}")
        if overlap_ip: print(f"    I-P overlap: {list(overlap_ip)}")
    print("-" * 20)
