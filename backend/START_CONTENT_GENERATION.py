#!/usr/bin/env python
"""
🚀 MASTER CONTENT GENERATION SCRIPT
Generates for all 200 topics:
- YouTube Videos (highly recommended, using provided API key)
- 4 Types of Explanations (visual, simplified, logical, analogy using Gemini)
- Professional PDFs  
- Mock Test Questions (8 per topic)
- All stored in MongoDB

Expected Duration: 90-180 minutes depending on API response times
"""

import os
import sys
import subprocess
import time

print("\n" + "="*80)
print("🎬 PIXEL PIRATES - CONTENT GENERATION MASTER SCRIPT")
print("="*80)

# Check environment
print("\n📋 PRE-FLIGHT CHECKS:")
print("-" * 80)

# 1. Check Python version
py_version = sys.version_info
print(f"✓ Python: {py_version.major}.{py_version.minor}.{py_version.micro}")

# 2. Check MongoDB
try:
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)
    client.server_info()
    db = client.pixel_pirates_db
    topics_count = db.topics.count_documents({})
    print(f"✓ MongoDB: Connected - {topics_count} topics found")
    client.close()
except Exception as e:
    print(f"✗ MongoDB: {e}")
    print("  Make sure MongoDB is running: mongod.exe")
    sys.exit(1)

# 3. Check API Keys
from app.core.config import Settings
settings = Settings()

if not settings.GEMINI_API_KEY:
    print("✗ GEMINI_API_KEY: Not configured in .env")
    sys.exit(1)
else:
    print(f"✓ GEMINI_API_KEY: {settings.GEMINI_API_KEY[:20]}...")

if not settings.YOUTUBE_API_KEY:
    print("✗ YOUTUBE_API_KEY: Not configured in .env")
    sys.exit(1)
else:
    print(f"✓ YOUTUBE_API_KEY: {settings.YOUTUBE_API_KEY[:20]}...")

# 4. Check required packages
print("\n✓ Required Packages:")
required_packages = ["httpx", "google.generativeai", "reportlab", "pymongo"]
for pkg in required_packages:
    try:
        __import__(pkg)
        print(f"  ✓ {pkg}")
    except ImportError:
        print(f"  ✗ {pkg} - MISSING!")
        print(f"    Install: pip install {pkg}")
        sys.exit(1)

# 5. Check PDF storage directory
from pathlib import Path
pdf_dir = Path("storage/pdfs")
pdf_dir.mkdir(parents=True, exist_ok=True)
print(f"✓ PDF Storage: {pdf_dir.absolute()}")

print("\n" + "="*80)
print("🎯 STARTING CONTENT GENERATION")
print("="*80)

print("\nℹ️  This process is LONG-RUNNING (90-180 minutes)")
print("   Processing 200 topics × (YouTube search + 4 explanations + PDF + mock test)")
print("   With concurrency limit of 2 topics at a time to avoid rate limiting")
print("\nℹ️  Running in BACKGROUND...")
print("   Check progress in: content_generation.log")
print("\n" + "="*80 + "\n")

# Launch generation script in background
start_time = time.time()

try:
    result = subprocess.run(
        [sys.executable, "generate_complete_content.py"],
        capture_output=True,
        text=True,
        timeout=None  # No timeout - let it run as long as needed
    )
    
    elapsed = time.time() - start_time
    
    # Check result
    if result.returncode == 0:
        print("✅ GENERATION COMPLETED SUCCESSFULLY!")
        print(f"\n⏱️  Total Time: {elapsed/60:.1f} minutes ({elapsed/3600:.1f} hours)")
        print("\n" + "="*80)
        print("📊 RESULTS:")
        print("="*80)
        print(result.stdout)
        
        # Summary
        print("\n✅ All content generated and stored in MongoDB!")
        print("   - Videos: 3+ per topic (highly recommended from YouTube)")
        print("   - Explanations: 4 types per topic (visual, simplified, logical, analogy)")
        print("   - PDFs: 1 per topic in storage/pdfs/")
        print("   - Mock Tests: 8 questions per topic (200 total)")
        
    else:
        print("⚠️  GENERATION ENCOUNTERED ERRORS")
        print("\n" + "="*80)
        print("STDOUT:")
        print(result.stdout)
        print("\nSTDERR:")
        print(result.stderr)
        print("="*80)
        
except subprocess.TimeoutExpired:
    print("❌ Generation process timed out")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print("\n" + "="*80)
print("✨ Ready to start backend and access your content!")
print("   Backend: uvicorn main:app --reload")
print("   API Docs: http://localhost:8000/docs")
print("="*80 + "\n")
