from pymongo import MongoClient
db = MongoClient('mongodb://localhost:27017')['pixel_pirates']

# Check topic-95 - originally had broken: un6ZyFkqFKo, YS4e4q9oBaU, 446E-r0rXHI
old_broken = {'un6ZyFkqFKo', 'YS4e4q9oBaU', '446E-r0rXHI'}
t = db.topics.find_one({'id': 'topic-95'}, {'recommendedVideos': 1, '_id': 0})
vids = t.get('recommendedVideos', [])
print("topic-95 videos:")
for v in vids:
    yt_id = v.get('youtubeId', '')
    was_broken = yt_id in old_broken
    print(f"  youtubeId={yt_id}  {'STILL BROKEN' if was_broken else 'NEW'}")

# Check topic-1 - originally had broken: 1UzSDMJRh8c, hnuPVeg51wE, Gx5qb1uHss4
old_broken2 = {'1UzSDMJRh8c', 'hnuPVeg51wE', 'Gx5qb1uHss4'}
t2 = db.topics.find_one({'id': 'topic-1'}, {'recommendedVideos': 1, '_id': 0})
vids2 = t2.get('recommendedVideos', [])
print("\ntopic-1 videos:")
for v in vids2:
    yt_id = v.get('youtubeId', '')
    was_broken = yt_id in old_broken2
    print(f"  youtubeId={yt_id}  {'STILL BROKEN' if was_broken else 'NEW'}")
