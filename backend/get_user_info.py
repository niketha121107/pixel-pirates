#!/usr/bin/env python
"""Get existing user info"""
from pymongo import MongoClient
from app.core.config import Settings

settings = Settings()
client = MongoClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DATABASE]

# Get first user
user = db.users.find_one({})
if user:
    print(f'User Email: {user.get("email")}')
    print(f'User Name: {user.get("name")}')
else:
    print('No users found')

client.close()
