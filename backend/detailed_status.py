#!/usr/bin/env python
"""Detailed content status check"""
import sys
sys.path.insert(0, ".")

from pymongo import MongoClient
from app.core.config import Settings

try:
    settings = Settings()
    client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
    db = client[settings.MONGODB_DATABASE]
    
    topics_total = db.topics.count_documents({})
    
    # Count topics with each type of content
    has_videos = db.topics.count_documents({"videos": {"$exists": True, "$ne": []}})
    has_explanations = db.topics.count_documents({"explanations": {"$exists": True, "$ne": []}})
    has_pdf = db.topics.count_documents({"pdf_path": {"$exists": True, "$ne": None}})
    has_all_three = db.topics.count_documents({
        "videos": {"$exists": True, "$ne": []},
        "explanations": {"$exists": True, "$ne": []},
        "pdf_path": {"$exists": True, "$ne": None}
    })
    
    mock_tests = db.mockTests.count_documents({})
    
    print("\n" + "="*70)
    print("CONTENT GENERATION DETAILED STATUS")
    print("="*70)
    print(f"\nTopics Total: {topics_total}")
    print(f"Topics with Videos: {has_videos} ({100*has_videos//topics_total if topics_total else 0}%)")
    print(f"Topics with Explanations: {has_explanations} ({100*has_explanations//topics_total if topics_total else 0}%)")
    print(f"Topics with PDFs: {has_pdf} ({100*has_pdf//topics_total if topics_total else 0}%)")
    print(f"Topics with ALL content: {has_all_three} ({100*has_all_three//topics_total if topics_total else 0}%)")
    print(f"\nMock Tests (individual questions): {mock_tests}")
    
    # Sample a fully populated topic
    sample = db.topics.find_one({
        "videos": {"$exists": True, "$ne": []},
        "explanations": {"$exists": True, "$ne": []},
        "pdf_path": {"$exists": True, "$ne": None}
    })
    
    if sample:
        print(f"\n" + "-"*70)
        print(f"SAMPLE FULLY POPULATED TOPIC: {sample.get('name', 'Unknown')}")
        print("-"*70)
        print(f"Language: {sample.get('language', 'N/A')}")
        print(f"Difficulty: {sample.get('difficulty', 'N/A')}")
        print(f"")
        print(f"Videos ({len(sample.get('videos', []))}): ")
        for i, v in enumerate(sample.get('videos', [])[:2]):
            print(f"  {i+1}. {v.get('title', 'N/A')[:60]}")
            print(f"     Channel: {v.get('channel', 'N/A')}")
        print(f"")
        print(f"Explanations ({len(sample.get('explanations', []))}): ")
        for e in sample.get('explanations', []):
            content_len = len(e.get('content', ''))
            print(f"  - {e.get('style', 'unknown')}: {content_len} chars")
        print(f"")
        print(f"PDF: {sample.get('pdf_path', 'N/A')}")
    else:
        # Show any topic that has some content
        sample = db.topics.find_one({"explanations": {"$exists": True, "$ne": []}})
        if sample:
            print(f"\n" + "-"*70)
            print(f"PARTIAL SAMPLE: {sample.get('name', 'Unknown')}")
            print(f"Has explanations: {len(sample.get('explanations', []))} types")
    
    print("\n" + "="*70)
    print("OVERALL PROGRESS")
    print("="*70)
    avg_completion = (has_videos + has_explanations + has_pdf) / (3 * topics_total) * 100 if topics_total else 0
    print(f"Average Completion: {avg_completion:.1f}%")
    
    if has_all_three >= 150:
        print("Status: EXCELLENT - Most topics complete!")
    elif has_all_three >= 100:
        print("Status: GOOD - Half way there!")
    elif has_explanations > 100:
        print("Status: PROGRESSING - Explanations being generated...")
    else:
        print("Status: INITIALIZING - Generation in progress...")
    
    print("="*70 + "\n")
    
    client.close()

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
