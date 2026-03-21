#!/usr/bin/env python3
"""Get first user credentials"""

import sys
sys.path.insert(0, ".")

import pymongo
import json

print("Getting first MongoDB user details")
print("=" * 60)

client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)
db = client["pixel_pirates"]

first_user = db.users.find_one()

if first_user:
    print("\nFirst User in MongoDB:")
    print(f"- Email: {first_user.get('email')}")
    print(f"- ID: {first_user.get('_id')}")
    print(f"- Name: {first_user.get('name', 'N/A')}")
    
    # Check for password-related fields
    if 'originalPassword' in first_user:
        print(f"- Original Password: {first_user.get('originalPassword')}")
    
    if 'password' in first_user:
        print(f"- Hashed Password stored: {len(first_user.get('password', ''))} chars")
    
    # List all keys
    print(f"\nAll fields: {list(first_user.keys())}")
else:
    print("No users found!")

print("\n" + "=" * 60)
