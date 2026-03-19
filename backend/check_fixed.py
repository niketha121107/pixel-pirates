from pymongo import MongoClient
db = MongoClient('mongodb://localhost:27017')['pixel_pirates']
topics = list(db.topics.find({}, {'id':1, 'topicName':1, 'recommendedVideos':1, '_id':0}))

fixed = 0
for t in topics[:10]:
    vids = t.get('recommendedVideos', [])
    has_yt = any(v.get('id', '').startswith('yt_') for v in vids)
    vid_count = len(vids)
    first_id = vids[0].get('youtubeId', 'none') if vids else 'none'
    status = 'FIXED' if has_yt else 'BROKEN'
    if has_yt:
        fixed += 1
    print(f"{t['id']}: {status} - {vid_count} vids, first: {first_id}")

total_fixed = sum(1 for t in topics if any(v.get('id', '').startswith('yt_') for v in t.get('recommendedVideos', [])))
print(f"\nTotal fixed: {total_fixed}/{len(topics)}")
