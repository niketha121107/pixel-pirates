#!/usr/bin/env python
"""Verify 200 exact topics with all content"""
from pymongo import MongoClient
from app.core.config import Settings

client = MongoClient(Settings().MONGODB_URL)
db = client[Settings().MONGODB_DATABASE]

v = db.topics.count_documents({"videos": {"$exists": True, "$ne": []}})
e = db.topics.count_documents({"explanations": {"$exists": True, "$ne": []}})
p = db.topics.count_documents({"pdf_path": {"$exists": True}})
m = db.mockTests.count_documents({})
t = db.topics.count_documents({})

print(f"\n{'='*70}")
print(f"PIXEL PIRATES - 200 EXACT TOPICS STATUS")
print(f"{'='*70}")
print(f"  Total Topics: {t}/200")
print(f"  Videos: {v}/200")
print(f"  Explanations (4 types each): {e}/200")
print(f"  PDFs: {p}/200")
print(f"  Mock Test Banks: {m}")
print(f"{'='*70}")

if v == 200 and e == 200 and p == 200:
    print(f"  ✅ ALL CONTENT 100% COMPLETE!\n")
else:
    print(f"  Completion: {int((v+e+p)/6)}%\n")

client.close()
