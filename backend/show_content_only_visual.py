#!/usr/bin/env python
"""Verify content-only visual explanations"""

from pymongo import MongoClient
from app.core.config import Settings

settings = Settings()
client = MongoClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DATABASE]

# Get sample topic
topic = db.topics.find_one({'name': 'Syntax & Variables'})

if topic:
    visual = str(topic.get('explanations', {}).get('visual', ''))
    
    print('\n' + '='*70)
    print('VISUAL EXPLANATION - CONTENT ONLY')
    print('='*70)
    print(f'\nTopic: {topic.get("name")} ({topic.get("language")})')
    print('\n' + '─'*70)
    print('CONTENT:')
    print('─'*70 + '\n')
    print(visual)
    print('\n' + '='*70)

client.close()
