#!/usr/bin/env python3
"""Debug MongoDB ID handling"""
from app.data import get_all_topics, initialize_data, _get_db
from bson.objectid import ObjectId

initialize_data()
topics = get_all_topics()

print("Topic from cache:")
topic = topics[0]
print(f"  Name: {topic.get('name')}")
print(f"  Fields: {list(topic.keys())}")
print(f"  'id' field: {topic.get('id')}")
print(f"  '_id' in topic? {bool('_id' in topic)}")

# Connect directly to MongoDB to check raw format
db = _get_db()
topics_collection = db['topics']

# Get one raw topic
raw_topic = topics_collection.find_one({})
print(f"\nRaw topic from MongoDB:")
print(f"  _id: {raw_topic.get('_id')} (type: {type(raw_topic.get('_id')).__name__})")
print(f"  name: {raw_topic.get('name')}")

# Test update with ObjectId
print(f"\nTesting update...")
test_id = raw_topic.get('_id')
print(f"  Query: {{'_id': {test_id}}}")

result = topics_collection.update_one(
    {"_id": test_id},
    {"$set": {"test_field": "test_value"}}
)
print(f"  Modified count: {result.modified_count}")
print(f"  ✓ Update successful" if result.modified_count > 0 else "  ✗ Update failed")

# Clean up
topics_collection.update_one({"_id": test_id}, {"$unset": {"test_field": ""}})
