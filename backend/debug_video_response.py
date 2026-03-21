#!/usr/bin/env python
"""Debug backend video response"""
import requests
import json

print("=" * 80)
print("DEBUGGING BACKEND VIDEO RESPONSE")
print("=" * 80)

# Test 1: Check if backend is running
print("\n✓ Test 1: Backend Connectivity")
try:
    r = requests.get("http://localhost:5000/health", timeout=5)
    print(f"  ✅ Backend responding: {r.status_code}")
except Exception as e:
    print(f"  ❌ Backend not responding: {e}")
    print("  Start backend with: python -m uvicorn main:app --reload")
    exit(1)

# Test 2: Get first topic
print("\n✓ Test 2: Fetching first topic")
try:
    r = requests.get("http://localhost:5000/api/topics/1")
    
    if r.status_code == 401:
        print("  ⚠️  Authorization required (expected - need login token)")
        print("  Trying to get topic list instead...")
        r = requests.get("http://localhost:5000/api/topics")
    
    if r.status_code == 200:
        data = r.json()
        print(f"  ✅ Got response: {r.status_code}")
        
        # Check data structure
        if isinstance(data, dict) and 'data' in data:
            topic = data['data']
        else:
            topic = data
        
        print(f"  Topic Name: {topic.get('topicName', 'N/A')}")
        
        # Check for videos
        videos = topic.get('recommendedVideos', [])
        print(f"  Recommended Videos: {len(videos)} found")
        
        if videos:
            for i, video in enumerate(videos[:2], 1):
                print(f"\n    Video {i}:")
                print(f"      YouTube ID: {video.get('youtubeId', 'MISSING')}")
                print(f"      Title: {video.get('title', 'N/A')[:60]}")
                print(f"      Channel: {video.get('channel', 'N/A')}")
        else:
            print("  ❌ NO VIDEOS IN RESPONSE!")
        
        # Full response dump
        print(f"\n  Full response keys: {list(topic.keys())}")
        
    else:
        print(f"  ❌ Error: {r.status_code}")
        print(f"  Response: {r.text[:200]}")
        
except Exception as e:
    print(f"  ❌ Error: {e}")

# Test 3: Check database directly
print("\n✓ Test 3: Checking MongoDB directly")
try:
    import asyncio
    from motor.motor_asyncio import AsyncIOMotorClient
    
    async def check_db():
        client = AsyncIOMotorClient("mongodb://localhost:27017/")
        db = client['pixel_pirates']
        
        # Get first topic
        topic = await db.topics.find_one({})
        
        if topic:
            print(f"  ✅ Found topic in DB: {topic.get('topicName', 'Unknown')}")
            
            videos = topic.get('recommendedVideos', [])
            print(f"  Videos in DB: {len(videos)}")
            
            if videos:
                for i, v in enumerate(videos[:2], 1):
                    print(f"    Video {i}: {v.get('youtubeId', 'MISSING')} - {v.get('title', 'N/A')[:40]}")
            else:
                print("  ❌ NO VIDEOS IN DATABASE!")
        else:
            print("  ❌ No topics found in database!")
    
    asyncio.run(check_db())
    
except ImportError:
    print("  ⚠️  Motor not installed - skipping direct DB check")
except Exception as e:
    print(f"  ⚠️  DB check error: {e}")

print("\n" + "=" * 80)
print("DEBUG COMPLETE")
print("=" * 80)
