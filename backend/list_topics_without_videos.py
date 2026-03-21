#!/usr/bin/env python3
"""Get list of topics without videos"""
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['pixel_pirates']

# Get topics without videos
topics_without = list(db.topics.find(
    {"videos": {"$exists": False}}
).sort("topicName", 1))

print(f"Found {len(topics_without)} topics without videos:\n")

for topic in topics_without:
    name = topic.get('topicName', topic.get('name', 'Unknown'))
    print(f"  • {name}")
