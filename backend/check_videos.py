"""Check status of YouTube videos across all topics."""
from pymongo import MongoClient

db = MongoClient('mongodb://localhost:27017')['pixel_pirates']
topics = list(db.topics.find({}, {'id':1, 'topicName':1, 'language':1, 'recommendedVideos':1, '_id':0}))

total = len(topics)
no_videos = []
has_videos = []
all_vid_ids = set()

for t in topics:
    vids = t.get('recommendedVideos', [])
    vid_ids = [v.get('youtubeId','') for v in vids if v.get('youtubeId')]
    if not vid_ids:
        no_videos.append(f"{t['id']}: {t.get('topicName','')} ({t.get('language','')})")
    else:
        has_videos.append({'id': t['id'], 'name': t.get('topicName',''), 'lang': t.get('language',''), 'vid_count': len(vid_ids), 'vids': vid_ids})
        all_vid_ids.update(vid_ids)

print(f"Total topics: {total}")
print(f"With videos: {len(has_videos)}")
print(f"Without videos: {len(no_videos)}")
print(f"Unique video IDs: {len(all_vid_ids)}")

if no_videos:
    print("\n--- Topics without videos ---")
    for n in no_videos:
        print(f"  {n}")

# Check which videos are embeddable using YouTube API
from dotenv import load_dotenv
import os, requests
load_dotenv()

api_key = os.getenv('YOUTUBE_API_KEY')
if not api_key:
    print("\nNo YOUTUBE_API_KEY found, cannot verify embeddability")
    exit()

print(f"\nChecking {len(all_vid_ids)} unique video IDs for embeddability...")

# Batch check in groups of 50
vid_list = list(all_vid_ids)
broken = []
not_embeddable = []
ok_count = 0

for i in range(0, len(vid_list), 50):
    batch = vid_list[i:i+50]
    ids_str = ','.join(batch)
    url = f"https://www.googleapis.com/youtube/v3/videos?part=status,snippet&id={ids_str}&key={api_key}"
    resp = requests.get(url)
    data = resp.json()
    
    found_ids = set()
    for item in data.get('items', []):
        vid_id = item['id']
        found_ids.add(vid_id)
        status_info = item.get('status', {})
        embeddable = status_info.get('embeddable', False)
        if not embeddable:
            not_embeddable.append(vid_id)
        else:
            ok_count += 1
    
    # IDs not returned = deleted/private videos
    for vid_id in batch:
        if vid_id not in found_ids:
            broken.append(vid_id)

print(f"\nResults:")
print(f"  OK (embeddable): {ok_count}")
print(f"  Not embeddable: {len(not_embeddable)}")
print(f"  Deleted/private: {len(broken)}")

# Map broken IDs back to topics
all_broken = set(broken + not_embeddable)
if all_broken:
    print(f"\n--- Topics with broken/non-embeddable videos ---")
    for h in has_videos:
        bad = [v for v in h['vids'] if v in all_broken]
        if bad:
            print(f"  {h['id']}: {h['name']} ({h['lang']}) - {len(bad)}/{h['vid_count']} broken: {bad}")
