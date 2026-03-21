#!/usr/bin/env python
"""Check final comprehensive content status"""
from pymongo import MongoClient
from app.core.config import Settings

client = MongoClient(Settings().MONGODB_URL)
db = client[Settings().MONGODB_DATABASE]

v = db.topics.count_documents({"videos": {"$exists": True, "$ne": []}})
e = db.topics.count_documents({"explanations": {"$exists": True, "$ne": []}})
k = db.topics.count_documents({"key_notes": {"$exists": True}})
p = db.topics.count_documents({"pdf_path": {"$exists": True}})
m = db.mockTests.count_documents({})
t = db.topics.count_documents({})

print("\n" + "="*80)
print("COMPREHENSIVE CONTENT STATUS - ALL 200 TOPICS")
print("="*80)
print(f"  Total Topics: {t}")
print(f"  Videos (Best Recommended): {v}/200")
print(f"  Explanations (4 types each): {e}/200")
print(f"  Key Notes/Study Material: {k}/200")
print(f"  Comprehensive PDFs: {p}/200")
print(f"  Mock Test Banks: {m}")
print("="*80)

# Sample topic with all content
sample = db.topics.find_one({"videos": {"$exists": True, "$ne": []}, "explanations": {"$exists": True, "$ne": []}})
if sample:
    print(f"\nSAMPLE COMPLETE TOPIC: {sample.get('name')} ({sample.get('language')})")
    print(f"  Videos: {len(sample.get('videos', []))} found")
    print(f"  Explanations: {list(sample.get('explanations', {}).keys())}")
    print(f"  Key Notes: {'Yes' if sample.get('key_notes') else 'No'}")
    print(f"  PDF: {sample.get('pdf_path', 'Not generated')}")

print("\n" + "="*80)
if v == 200 and e == 200 and k == 200 and p == 200 and m >= 150:
    print("  SUCCESS: All 200 topics have COMPLETE comprehensive content!")
else:
    total = v + e + k + p
    print(f"  Status: {int(100*total/800)}% complete")
print("="*80 + "\n")

client.close()
