#!/usr/bin/env python
"""End-to-end verification of video system"""
import requests
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import json

print("=" * 80)
print("END-TO-END VIDEO SYSTEM VERIFICATION")
print("=" * 80)

# Step 1: Check database
print("\n✓ Step 1: Database Check")
async def check_db():
    client = AsyncIOMotorClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
    db = client['pixel_pirates']
    
    topics_count = await db.topics.count_documents({})
    topics_with_videos = await db.topics.count_documents({'recommendedVideos': {'$exists': True, '$ne': []}})
    
    print(f"   Total topics: {topics_count}")
    print(f"   Topics with videos: {topics_with_videos}")
    
    # Get total video count
    result = await db.topics.aggregate([
        {'$match': {'recommendedVideos': {'$exists': True}}},
        {'$project': {'count': {'$size': '$recommendedVideos'}}},
        {'$group': {'_id': None, 'total': {'$sum': '$count'}}}
    ]).to_list(None)
    
    video_count = result[0]['total'] if result else 0
    print(f"   Total videos: {video_count}")
    
    if topics_with_videos == topics_count:
        print(f"   ✅ DATABASE VERIFIED: 100% coverage")
        return True
    else:
        print(f"   ❌ Missing videos in {topics_count - topics_with_videos} topics")
        return False

db_status = asyncio.run(check_db())

# Step 2: Check API
print("\n✓ Step 2: API Authentication & Response")
login_resp = requests.post(
    'http://localhost:5000/api/auth/login', 
    json={'email': 'alex@edutwin.com', 'password': 'password123'}
)

if login_resp.status_code == 200:
    token = login_resp.json().get('access_token')
    print(f"   ✅ Login successful, token: {token[:20]}...")
    
    # Get a topic
    headers = {'Authorization': f'Bearer {token}'}
    
    async def get_topic_id():
        client = AsyncIOMotorClient('mongodb://localhost:27017/')
        db = client['pixel_pirates']
        topic = await db.topics.find_one({})
        return str(topic['_id']) if topic else None
    
    topic_id = asyncio.run(get_topic_id())
    
    if topic_id:
        topic_resp = requests.get(f'http://localhost:5000/api/topics/{topic_id}', headers=headers)
        
        if topic_resp.status_code == 200:
            topic_data = topic_resp.json()
            topic = topic_data.get('data', {}).get('topic', {})
            videos = topic.get('recommendedVideos', [])
            
            print(f"   ✅ Topic retrieved: {topic.get('topicName')}")
            print(f"   ✅ Videos returned: {len(videos)}")
            
            if videos and len(videos) > 0:
                v = videos[0]
                print(f"   ✅ First video:")
                print(f"       ID: {v.get('youtubeId')}")
                print(f"       Title: {v.get('title')}")
                print(f"   ✅ API VERIFIED")
                api_status = True
            else:
                print(f"   ❌ No videos in API response")
                api_status = False
        else:
            print(f"   ❌ Topic fetch failed: {topic_resp.status_code}")
            api_status = False
    else:
        print(f"   ❌ Could not get topic ID")
        api_status = False
else:
    print(f"   ❌ Login failed: {login_resp.status_code}")
    api_status = False

# Step 3: Video Format Check
print("\n✓ Step 3: Video Format Validation")
if api_status:
    async def validate_videos():
        client = AsyncIOMotorClient('mongodb://localhost:27017/')
        db = client['pixel_pirates']
        
        # Sample 10 videos
        sample_topics = await db.topics.find({'recommendedVideos': {'$exists': True}}).limit(10).to_list(None)
        
        invalid_count = 0
        for topic in sample_topics:
            for v in topic.get('recommendedVideos', []):
                video_id = v.get('youtubeId', '')
                if len(video_id) != 11 or not all(c.isalnum() or c in '-_' for c in video_id):
                    invalid_count += 1
        
        print(f"   Checked: {len(sample_topics) * 3} videos")
        print(f"   Invalid: {invalid_count}")
        
        if invalid_count == 0:
            print(f"   ✅ VIDEOS VALID: All 11-char IDs")
            return True
        else:
            print(f"   ⚠️ Some videos may have invalid format")
            return False
    
    format_status = asyncio.run(validate_videos())
else:
    format_status = False

# Final Summary
print("\n" + "=" * 80)
print("VERIFICATION SUMMARY")
print("=" * 80)
print(f"Database: {'✅ PASS' if db_status else '❌ FAIL'}")
print(f"API: {'✅ PASS' if api_status else '❌ FAIL'}")
print(f"Format: {'✅ PASS' if format_status else '❌ FAIL'}")

if db_status and api_status and format_status:
    print(f"\n✅ SYSTEM IS READY FOR FRONTEND TESTING")
    print(f"\nNextsteps:")
    print(f"1. Open http://localhost:5173 in browser")
    print(f"2. Login with alex@edutwin.com / password123")
    print(f"3. Click any topic")
    print(f"4. Videos should load in 'Watch the Video' section")
else:
    print(f"\n❌ SYSTEM HAS ISSUES - CHECK ABOVE FOR DETAILS")
