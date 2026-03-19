from pymongo import MongoClient
db = MongoClient('mongodb://localhost:27017')['pixel_pirates']
all_t = list(db.topics.find({}, {'id':1, 'recommendedVideos':1, '_id':0}))
no_video_ids = [t['id'] for t in all_t if not any(v.get('youtubeId') for v in t.get('recommendedVideos', []))]
print(f'Removing {len(no_video_ids)} topics without YouTube videos...')
result = db.topics.delete_many({'id': {'$in': no_video_ids}})
print(f'Deleted: {result.deleted_count}')
remaining = db.topics.count_documents({})
print(f'Remaining topics: {remaining}')
