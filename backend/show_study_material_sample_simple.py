#!/usr/bin/env python
"""Display detailed sample study material"""

import sys
from pymongo import MongoClient
from app.core.config import Settings

# Handle encoding issues
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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
    
    # Display each section (abbreviated for display)
    sections_order = ['overview', 'explanation', 'syntax', 'example', 'domain_usage', 'advantages', 'disadvantages']
    
    for section in sections_order:
        if section in sm:
            content = str(sm[section])
            
            # Display section header and first 400 chars
            print(f'\n[{section.upper().replace("_", " ")}]')
            print('-'*70)
            
            # Show first paragraphs
            lines = content.split('\n')[:6]  # First 6 lines
            for line in lines:
                if line.strip():
                    print(line[:80])  # Limit line width
            
            # Show content size
            print(f'... (Total: {len(content)} characters)')
            print()

client.close()
