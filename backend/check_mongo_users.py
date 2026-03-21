#!/usr/bin/env python3
"""Check MongoDB users"""

import sys
sys.path.insert(0, ".")

import pymongo
from app.data import load_from_mongodb, MOCK_USERS

print("Checking MongoDB Utils")
print("=" * 60)

print("\n1. Connecting to MongoDB...")
try:
    client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)
    client.admin.command("ping")
    print("   ✅ MongoDB is running")
    
    db = client["pixel_pirates"]
    
    # Check users collection
    user_count = db.users.count_documents({})
    print(f"\n2. Users in mongodb: {user_count}")
    
    if user_count > 0:
        first_user = db.users.find_one()
        print(f"   First user email: {first_user.get('email', 'N/A')}")
        print(f"   User ID: {first_user.get('_id', 'N/A')}")
    
    # Check topics collection
    topic_count = db.topics.count_documents({})
    print(f"\n3. Topics in MongoDB: {topic_count}")
    
except Exception as e:
    print(f"   ❌ MongoDB error: {e}")
    sys.exit(1)

print("\n4. Loading data into memory cache...")
load_from_mongodb()
print(f"   MOCK_USERS cache: {len(MOCK_USERS)} users")

if MOCK_USERS:
    first_email = list(MOCK_USERS.values())[0].get("email", "N/A")
    print(f"   First user email: {first_email}")

print("\n" + "=" * 60)
