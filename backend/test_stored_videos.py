#!/usr/bin/env python3
"""Test that stored database videos are being returned"""

import requests
import json

BASE_URL = "http://localhost:5000/api"

# Test login/register
login_data = {
    "email": "test@example.com",
    "password": "test123"
}

print("Testing Stored Video Retrieval")
print("=" * 60)

# Get token
print("\n1. Authenticating...")
resp = requests.post(f"{BASE_URL}/auth/login", json=login_data)

if resp.status_code != 200:
    # Try signup
    resp = requests.post(f"{BASE_URL}/auth/signup", json=login_data)

if resp.status_code == 200:
    token = resp.json()["data"].get("access_token", "")
    print(f"   ✅ Token obtained: {token[:20]}...")
else:
    print(f"   ❌ Auth failed: {resp.status_code}")
    exit(1)

# Get topics list
print("\n2. Fetching topics list...")
headers = {"Authorization": f"Bearer {token}"}
resp = requests.get(f"{BASE_URL}/topics", headers=headers)

if resp.status_code == 200:
    topics = resp.json()["data"].get("topics", [])
    print(f"   ✅ Retrieved {len(topics)} topics")
    
    if topics:
        # Get first topic details
        first_topic = topics[0]
        topic_id = first_topic["id"]
        topic_name = first_topic["topicName"]
        
        print(f"\n3. Fetching details for: {topic_name}")
        resp = requests.get(f"{BASE_URL}/topics/{topic_id}", headers=headers)
        
        if resp.status_code == 200:
            topic_data = resp.json()["data"].get("topic", {})
            videos = topic_data.get("recommendedVideos", [])
            
            print(f"   Videos returned: {len(videos)}")
            
            if videos:
                print("\n4. Sample Videos:")
                for i, video in enumerate(videos[:3], 1):
                    print(f"\n   Video {i}:")
                    print(f"   - Title: {video.get('title', 'N/A')[:60]}")
                    print(f"   - YouTube ID: {video.get('youtubeId', 'N/A')}")
                    print(f"   - Channel: {video.get('channel', 'N/A')}")
                    print(f"   - Views: {video.get('views', 0):,}")
                
                print("\n   ✅ SUCCESS: Stored videos are being returned!")
            else:
                print("   ⚠️ No videos found for this topic")
        else:
            print(f"   ❌ Topic fetch failed: {resp.status_code}")
else:
    print(f"   ❌ Topics fetch failed: {resp.status_code}")

print("\n" + "=" * 60)
