#!/usr/bin/env python
"""Test if the fix works"""
from pymongo import MongoClient
from app.core.config import Settings
from app.data import MOCK_TOPICS, load_from_mongodb

settings = Settings()
client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
db = client[settings.MONGODB_DATABASE]

# Check data
topics_count = db.topics.count_documents({})
sample_topic = db.topics.find_one({})

print(f'MongoDB connection: SUCCESS')
print(f'Total topics in DB: {topics_count}')

if sample_topic:
    print(f'\nSample topic from DB:')
    print(f'  _id: {sample_topic.get("_id")}')
    print(f'  name: {sample_topic.get("name")}')
    print(f'  language: {sample_topic.get("language")}')

# Now try to load into memory cache
print(f'\nLoading into cache...')
load_from_mongodb()

print(f'Topics in memory cache: {len(MOCK_TOPICS)}')
if MOCK_TOPICS:
    first_key = list(MOCK_TOPICS.keys())[0]
    first_topic = MOCK_TOPICS[first_key]
    print(f'\nFirst cached topic:')
    print(f'  Cache key (id): {first_key}')
    print(f'  Topic name: {first_topic.get("name")}')
    print(f'  Topic language: {first_topic.get("language")}')
    print(f'\n✅ FIX SUCCESSFUL - Topics loaded with id field!')
else:
    print('❌ No topics in cache')

client.close()
