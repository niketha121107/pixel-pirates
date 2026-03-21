from pymongo import MongoClient
from app.core.config import Settings

settings = Settings()
client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
db = client[settings.MONGODB_DATABASE]

# Check one topic to see what fields it has
topic = db.topics.find_one({})
if topic:
    print('\n=== CURRENT TOPIC STRUCTURE ===')
    print('Fields in current topic:')
    for key in topic.keys():
        if key != '_id':
            print(f'  - {key}')
    
    # Check if study_material exists
    if 'study_material' in topic:
        print(f'\n✓ study_material exists')
        sm = topic['study_material']
        if isinstance(sm, dict):
            print(f'  Sections: {list(sm.keys())}')
            for section, content in sm.items():
                chars = len(str(content))
                print(f'    - {section}: {chars} chars')
    else:
        print(f'\n✗ study_material NOT found')
    
    # Count how many topics have study_material
    count_with_sm = db.topics.count_documents({'study_material': {'$exists': True}})
    total = db.topics.count_documents({})
    print(f'\n=== DATABASE STATUS ===')
    print(f'Topics with study_material: {count_with_sm}/{total}')
else:
    print('No topics found in database')

client.close()
