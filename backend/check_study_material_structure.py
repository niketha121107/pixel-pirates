#!/usr/bin/env python
"""Check current study material structure"""

from pymongo import MongoClient
from app.core.config import Settings

settings = Settings()
client = MongoClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DATABASE]

topic = db.topics.find_one()
if topic and 'study_material' in topic:
    sm = topic.get('study_material', {})
    print('\nCurrent Study Material Structure:')
    print(f'Topic: {topic.get("name")}')
    print(f'Language: {topic.get("language")}')
    print(f'\nKeys present: {list(sm.keys())}')
    print(f'\nContent samples:')
    for key in sm.keys():
        content = str(sm.get(key, ''))
        size = len(content)
        preview = content[:80] if len(content) > 80 else content
        print(f'\n  {key}:')
        print(f'    Size: {size} chars')
        print(f'    Preview: {preview}...')
else:
    print('No study material found or structure is empty')

client.close()
