#!/usr/bin/env python
"""Quick status check and write to file"""
from pymongo import MongoClient
from app.core.config import Settings

client = MongoClient(Settings().MONGODB_URL)
db = client[Settings().MONGODB_DATABASE]

v = db.topics.count_documents({"videos": {"$exists": True, "$ne": []}})
e = db.topics.count_documents({"explanations": {"$exists": True, "$ne": []}})
k = db.topics.count_documents({"key_notes": {"$exists": True, "$ne": None, "$ne": ""}})
p = db.topics.count_documents({"pdf_path": {"$exists": True}})
m = db.mockTests.count_documents({})

status = f"""
================================================================================
COMPREHENSIVE CONTENT - ALL 200 TOPICS FINAL STATUS
================================================================================
Total Topics: 200

Content Generated:
  Videos (Best Recommended): {v}/200 ({int(100*v/200)}%)
  Explanations (4 types each): {e}/200 ({int(100*e/200)}%)
  Key Notes/Study Material: {k}/200 ({int(100*k/200)}%)
  Comprehensive PDFs: {p}/200 ({int(100*p/200)}%)
  Mock Test Banks: {m}

================================================================================
COMPLETION STATUS: {int((v+e+k+p)/8)}%
================================================================================
"""

# Write to file
with open("_final_status.txt", "w") as f:
    f.write(status)

print(status)
client.close()
