#!/usr/bin/env python
"""Check content generation status in MongoDB"""
import sys
sys.path.insert(0, ".")

from pymongo import MongoClient
from app.core.config import Settings

try:
    settings = Settings()
    client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
    db = client[settings.MONGODB_DATABASE]
    
    # Check collections
    topics_count = db.topics.count_documents({})
    
    # Check if topics have content
    completed_topics = db.topics.count_documents({
        "videos": {"$exists": True, "$ne": []},
        "explanations": {"$exists": True, "$ne": []},
        "pdf_path": {"$exists": True, "$ne": None}
    })
    
    mock_tests_count = db.mockTests.count_documents({})
    
    print("\n" + "="*70)
    print("📊 CONTENT GENERATION STATUS")
    print("="*70)
    print(f"\nTopics in Database: {topics_count}")
    print(f"Topics with Complete Content: {completed_topics}")
    print(f"Mock Tests Generated: {mock_tests_count}")
    
    # Sample a topic to see what content was generated
    sample = db.topics.find_one({})
    if sample:
        print(f"\n📝 Sample Topic: {sample.get('name', 'Unknown')}")
        print(f"   Language: {sample.get('language', 'N/A')}")
        print(f"   Difficulty: {sample.get('difficulty', 'N/A')}")
        
        if "videos" in sample:
            print(f"   Videos: {len(sample.get('videos', []))} found")
            if sample['videos']:
                print(f"           First video: {sample['videos'][0].get('title', 'N/A')[:60]}")
        
        if "explanations" in sample:
            expl = sample.get('explanations', [])
            print(f"   Explanations: {len(expl)} types found")
            for e in expl:
                print(f"                 - {e.get('style', 'unknown')}: {len(e.get('content', ''))} chars")
        
        if "pdf_path" in sample:
            print(f"   PDF: {sample.get('pdf_path', 'N/A')}")
    
    print("\n" + "="*70)
    
    if completed_topics > 0:
        percent = (completed_topics / topics_count * 100) if topics_count > 0 else 0
        print(f"✅ Progress: {percent:.1f}% complete ({completed_topics}/{topics_count})")
    else:
        print("⏳ Generation starting or in progress...")
    
    print("="*70 + "\n")
    
    client.close()

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
