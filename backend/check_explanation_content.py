#!/usr/bin/env python
"""Check explanation content length"""
from pymongo import MongoClient
from app.core.config import Settings

settings = Settings()
client = MongoClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DATABASE]

# Get first Python topic
topic = db.topics.find_one({'language': 'Python', 'name': 'Syntax & Variables'})
if topic and 'explanations' in topic:
    expl = topic['explanations']
    print("Explanation content samples:")
    for style, content in expl.items():
        if isinstance(content, dict):
            text = content.get('content', '')
        else:
            text = str(content)
        print(f"\n{style.upper()}:")
        print(f"  Type: {type(content).__name__}")
        print(f"  Length: {len(text)} chars")
        print(f"  Content: {text[:200]}...")

client.close()
