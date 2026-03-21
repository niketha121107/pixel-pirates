#!/usr/bin/env python
"""PIXEL PIRATES - FINAL CONTENT GENERATION REPORT"""

import sys  
sys.path.insert(0, ".")

from pymongo import MongoClient
from app.core.config import Settings
from pathlib import Path

try:
    settings = Settings()
    client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
    db = client[settings.MONGODB_DATABASE]
    
    print("\n" + "="*80)
    print("                PIXEL PIRATES - CONTENT GENERATION REPORT")
    print("="*80)
    
    # Database stats
    topics_count = db.topics.count_documents({})
    mock_tests_count = db.mockTests.count_documents({})
    
    print("\n[DATABASE INVENTORY]")
    print(f"  • Total Topics: {topics_count}")
    print(f"  • Mock Test Sets: {mock_tests_count}")
    
    # Content breakdown
    print("\n[CONTENT BY TYPE]")
    
    videos_count = db.topics.count_documents({"videos": {"$exists": True, "$ne": []}})
    explan_count = db.topics.count_documents({"explanations": {"$exists": True, "$ne": []}})
    pdf_count = db.topics.count_documents({"pdf_path": {"$exists": True, "$ne": None}})
    
    print(f"  Videos:       {videos_count:3d}/{topics_count} topics  ({100*videos_count//topics_count if topics_count else 0}%)")
    print(f"  Explanations: {explan_count:3d}/{topics_count} topics  ({100*explan_count//topics_count if topics_count else 0}%)")
    print(f"  PDFs:         {pdf_count:3d}/{topics_count} topics  ({100*pdf_count//topics_count if topics_count else 0}%)")
    
    # Explanation types
    if explan_count > 0:
        sample = db.topics.find_one({"explanations": {"$exists": True, "$ne": []}})
        if sample and "explanations" in sample:
            styles_found = {e.get("style", "unknown") for e in sample["explanations"]}
            print(f"\n  Explanation Types Generated: {', '.join(sorted(styles_found))}")
    
    # PDF storage
    pdf_dir = Path("storage/pdfs")
    if pdf_dir.exists():
        pdf_files = list(pdf_dir.glob("*.pdf"))
        print(f"\n  PDFs on Disk: {len(pdf_files)} files")
        if pdf_files:
            total_size = sum(f.stat().st_size for f in pdf_files) / (1024*1024)
            print(f"  PDF Total Size: {total_size:.1f} MB")
    
    # Sample topics with content
    print("\n[SAMPLE TOPICS WITH GENERATED CONTENT]")
    samples = db.topics.find({"explanations": {"$exists": True, "$ne": []}}).limit(5)
    for i, topic in enumerate(samples, 1):
        print(f"\n  {i}. {topic.get('name', 'Unknown')} ({topic.get('language', '?')})")
        
        if "videos" in topic and topic["videos"]:
            print(f"     Videos: {len(topic['videos'])} x YouTube")
            for v in topic["videos"][:1]:
                title = v.get("title", "N/A")[:50]
                print(f"       - {title}")
        
        if "explanations" in topic:
            expl = topic["explanations"]
            print(f"     Explanations: {len(expl)} types")
            for e in expl:
                print(f"       - {e.get('style', '?')}: {len(e.get('content', '')) } chars")
        
        if "pdf_path" in topic and topic["pdf_path"]:
            print(f"     PDF: {Path(topic['pdf_path']).name}")
    
    # Summary
    print("\n" + "="*80)
    print("[SUMMARY]")
    print("="*80)
    
    avg_completion = (videos_count + explan_count + pdf_count) / (3 * topics_count * 100) if topics_count else 0
    overall_percent = int((videos_count + explan_count + pdf_count) / (3 * topics_count) * 100) if topics_count else 0
    
    print(f"\nOverall Completion: {overall_percent}%")
    print(f"  • YouTube Videos: {videos_count} topics")
    print(f"  • Explanations (4 types): {explan_count} topics")
    print(f"  • Study PDFs: {pdf_count} topics")
    print(f"  • Mock Tests: {mock_tests_count} question banks")
    
    print("\n[NEXT STEPS]")
    print("1. Start backend server:")
    print("   cd e:\\pixel pirates\\pixel-pirates\\backend")
    print("   uvicorn main:app --reload")
    print("\n2. API endpoints now available:")
    print("   - GET /api/topics (all 200 topics)")
    print("   - GET /api/topics/{id} (single topic)")
    print("   - GET /api/topics/{id}/videos (YouTube videos)")
    print("   - GET /api/study-materials/all-topics/pdf-info (all PDFs)")
    print("   - API Docs: http://localhost:8000/docs")
    print("\n3. Access frontend:")
    print("   http://localhost:5173")
    
    print("\n" + "="*80 + "\n")
    
    client.close()

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
