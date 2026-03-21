#!/usr/bin/env python
"""
Final PDF Generation Verification Report
"""
import os
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
db = client["pixel_pirates"]

topics = list(db.topics.find({}, {"topicName": 1, "pdf_filename": 1, "_id": 1}).sort("topicName", 1))

print("\n" + "="*80)
print("FINAL PDF GENERATION VERIFICATION - ALL 99 TOPICS")
print("="*80 + "\n")

valid_count = 0
invalid_topics = []

for i, topic in enumerate(topics, 1):
    name = topic.get("topicName", "Unknown")
    filename = topic.get("pdf_filename", "")
    pdf_path = os.path.join("storage/pdfs", filename) if filename else ""
    
    if pdf_path and os.path.exists(pdf_path):
        size_kb = os.path.getsize(pdf_path) / 1024
        print(f"{i:2d}. [OK] {name:40s} ({size_kb:.1f}KB)")
        valid_count += 1
    else:
        print(f"{i:2d}. [XX] {name:40s} (MISSING)")
        invalid_topics.append(name)

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Total Topics: {len(topics)}")
print(f"With Valid PDFs: {valid_count}")
print(f"Missing PDFs: {len(invalid_topics)}")
print(f"Coverage: {100*valid_count/len(topics):.1f}%")

if invalid_topics:
    print(f"\nMissing PDFs for:")
    for topic in invalid_topics:
        print(f"  - {topic}")
else:
    print(f"\n*** SUCCESS: All {len(topics)} topics have valid PDFs ***")

print("="*80 + "\n")
