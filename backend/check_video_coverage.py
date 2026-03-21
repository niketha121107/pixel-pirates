#!/usr/bin/env python3
"""Check video coverage in database"""
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['pixel_pirates']

with_videos = db.topics.count_documents({'videos': {'$exists': True}})
without_videos = db.topics.count_documents({'videos': {'$exists': False}})
total = db.topics.count_documents({})

print(f'Topics with videos: {with_videos}')
print(f'Topics without videos: {without_videos}')
print(f'Total topics: {total}')
print(f'Coverage: {(with_videos/total*100):.1f}%')

# Show first 3 topics with videos
print(f'\nSample topics with videos:')
topics = list(db.topics.find({'videos': {'$exists': True}}).limit(3))
for topic in topics:
    videos = topic.get('videos', [])
    name = topic.get('topicName', topic.get('name', 'Unknown'))
    print(f"  • {name}: {len(videos)} videos")
    if videos:
        title = videos[0].get('title', 'N/A')[:60]
        print(f"    Top: {title}")
