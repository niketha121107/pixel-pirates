#!/usr/bin/env python
"""Check what topic data exists in MongoDB"""
from pymongo import MongoClient
from app.core.config import Settings

settings = Settings()
client = MongoClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DATABASE]

# Get a sample topic
topic = db.topics.find_one({'language': 'Python'})
if topic:
    topic['_id'] = str(topic['_id'])
    # Print all fields
    fields = list(topic.keys())
    print('MongoDB Topic Fields:')
    for field in sorted(fields):
        value_type = type(topic[field]).__name__
        print(f'  - {field}: {value_type}')
    
    # Check if explanations exist
    has_expl = 'explanations' in topic
    print(f'\nExplanations: {has_expl}')
    if has_expl and topic['explanations']:
        if isinstance(topic['explanations'], dict):
            print(f'  Keys: {list(topic["explanations"].keys())}')
            for key, val in topic['explanations'].items():
                if isinstance(val, dict):
                    print(f'    {key}: {list(val.keys())}')
        else:
            print(f'  Type: {type(topic["explanations"]).__name__}')
    
    # Check if videos exist
    has_vid = 'videos' in topic
    print(f'\nVideos: {has_vid}')
    if has_vid and topic['videos']:
        print(f'  Count: {len(topic["videos"])}')
        if len(topic['videos']) > 0 and isinstance(topic['videos'][0], dict):
            print(f'  First item keys: {list(topic["videos"][0].keys())}')
    
    # Check if key_notes exist
    has_notes = 'key_notes' in topic
    print(f'\nKey Notes: {has_notes}')
    if has_notes:
        print(f'  Type: {type(topic["key_notes"]).__name__}')
        print(f'  Has content: {bool(topic["key_notes"])}')
        if topic['key_notes']:
            print(f'  First 100 chars: {str(topic["key_notes"])[:100]}...')
        
    # Check if study_material exist
    has_study = 'study_material' in topic
    print(f'\nStudy Material: {has_study}')
    if has_study:
        print(f'  Type: {type(topic["study_material"]).__name__}')
        if topic['study_material']:
            if isinstance(topic['study_material'], dict):
                print(f'  Keys: {list(topic["study_material"].keys())}')
            else:
                print(f'  First 100 chars: {str(topic["study_material"])[:100]}...')
else:
    print('No Python topic found')

client.close()
