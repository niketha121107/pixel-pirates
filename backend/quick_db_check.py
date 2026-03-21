#!/usr/bin/env python
"""Quick database status check"""
import subprocess
import sys

# Run the verification in a subprocess to avoid terminal state issues
code = '''
import sys
sys.path.insert(0, ".")
from pymongo import MongoClient
from app.core.config import Settings

settings = Settings()
client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
db = client[settings.MONGODB_DATABASE]

topics_count = db.topics.count_documents({})
leaderboard_count = db.leaderboard.count_documents({})

print(f"TOPICS: {topics_count}")
print(f"LEADERBOARD: {leaderboard_count}")

if leaderboard_count > 0:
    result = db.leaderboard.delete_many({})
    print(f"DELETED: {result.deleted_count}")

client.close()
'''

result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=".")
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
