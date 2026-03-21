#!/usr/bin/env python
"""Check current topic data structure"""
from pymongo import MongoClient
from app.core.config import Settings
import json

settings = Settings()
client = MongoClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DATABASE]

topic = db.topics.find_one({'language': 'Python', 'name': 'Syntax & Variables'})
if topic:
    print("Current Topic Structure:")
    print("="*80)
    print(f"name: {topic.get('name')}")
    print(f"language: {topic.get('language')}")
    print(f"\nvideos: {topic.get('videos')}")
    print(f"\nexplanations keys: {list(topic.get('explanations', {}).keys())}")
    print(f"\nkey_notes: {topic.get('key_notes')}")
    print(f"\nstudyMaterial (if exists): {topic.get('studyMaterial', 'NOT PRESENT')}")
    
    # Check what's in explanations
    visual = topic.get('explanations', {}).get('visual', '')
    print(f"\nVISUAL explanation preview:")
    print(visual[:200] if visual else "EMPTY")
    
    # Check videos
    vids = topic.get('videos', [])
    if vids:
        print(f"\nFirst video structure:")
        print(json.dumps(vids[0], indent=2, default=str))

client.close()
