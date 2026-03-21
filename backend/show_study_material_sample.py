#!/usr/bin/env python
"""Display detailed sample study material"""

from pymongo import MongoClient
from app.core.config import Settings

settings = Settings()
client = MongoClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DATABASE]

# Get a sample topic
topic = db.topics.find_one({'name': 'Syntax & Variables'})

if topic:
    sm = topic.get('study_material', {})
    
    print('\n' + '='*70)
    print('COMPREHENSIVE STUDY MATERIAL SAMPLE')
    print('='*70)
    print(f'\nTopic: {topic.get("name")} ({topic.get("language")})')
    print(f'Language: {topic.get("language")}')
    print(f'Difficulty: {topic.get("difficulty")}')
    print('='*70)
    
    # Display each section
    sections_order = ['overview', 'explanation', 'syntax', 'example', 'domain_usage', 'advantages', 'disadvantages']
    
    for section in sections_order:
        if section in sm:
            content = str(sm[section])
            print(f'\n{section.upper().replace("_", " ")}:')
            print('─'*70)
            print(content)
            print()

client.close()
