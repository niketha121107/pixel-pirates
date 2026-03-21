import os
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['pixel_pirates']

# Count valid PDFs
valid = 0
invalid = 0
missing = []

topics = list(db.topics.find({}, {'topicName': 1, 'pdf_path': 1}))

for topic in topics:
    pdf_path = topic.get('pdf_path')
    if pdf_path and os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 500:
        valid += 1
    else:
        invalid += 1
        if topic.get('topicName'):
            missing.append(topic.get('topicName'))

print(f'Total Topics: {len(topics)}')
print(f'Valid PDFs: {valid}')
print(f'Invalid/Missing PDFs: {invalid}')

if missing:
    print(f'\nMissing PDFs for ({len(missing)} topics):')
    for m in missing:
        print(f'  - {m}')
