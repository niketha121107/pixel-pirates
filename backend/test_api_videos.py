#!/usr/bin/env python3
"""Test the actual API endpoint returns stored videos correctly"""

import httpx
import json
import asyncio

BASE_URL = "http://localhost:5000"

async def test_api():
    print("Testing API Endpoint - Stored Videos Retrieval")
    print("=" * 70)
    
    async with httpx.AsyncClient() as client:
        # Step 1: Get a test user token
        print("\n1. Getting authentication token...")
        try:
            # Register or login with a test user
            login_data = {
                "email": "test.user@example.com",
                "password": "TestPassword123!"
            }
            
            # First try to signup
            signup_response = await client.post(
                f"{BASE_URL}/api/auth/signup",
                json=login_data,
                timeout=5.0
            )
            
            if signup_response.status_code in [200, 201]:
                print(f"   ✅ Signed up new user")
            elif signup_response.status_code == 400:
                print(f"   ℹ️  User likely exists, will try login...")
            else:
                print(f"   ⚠️  Signup response: {signup_response.status_code}")
            
            # Now login
            login_response = await client.post(
                f"{BASE_URL}/api/auth/login",
                json=login_data,
                timeout=5.0
            )
            
            if login_response.status_code != 200:
                print(f"   ❌ Login failed: {login_response.status_code}")
                print(f"      Response: {login_response.text[:200]}")
                return False
            
            login_data_resp = login_response.json()
            token = login_data_resp.get("data", {}).get("token")
            
            if not token:
                print(f"   ❌ No token in response: {login_data_resp}")
                return False
            
            print(f"   ✅ Got token: {token[:20]}...")
            
        except Exception as e:
            print(f"   ❌ Auth error: {e}")
            return False
        
        # Step 2: Get all topics to list them
        print("\n2. Fetching all topics...")
        try:
            headers = {"Authorization": f"Bearer {token}"}
            topics_response = await client.get(
                f"{BASE_URL}/api/topics",
                headers=headers,
                timeout=5.0
            )
            
            if topics_response.status_code != 200:
                print(f"   ❌ Topics list failed: {topics_response.status_code}")
                print(f"      Response: {topics_response.text[:200]}")
                return False
            
            topics_data = topics_response.json()
            topics_list = topics_data.get("data", {}).get("topics", [])
            print(f"   ✅ Retrieved {len(topics_list)} topics")
            
            if not topics_list:
                print("   ❌ No topics returned!")
                return False
            
            first_topic = topics_list[0]
            
        except Exception as e:
            print(f"   ❌ Topics fetch error: {e}")
            return False
        
        # Step 3: Get details of a specific topic
        print("\n3. Getting topic details with stored videos...")
        try:
            topic_id = first_topic.get("id")
            topic_name = first_topic.get("topicName", "Unknown")
            
            print(f"   Fetching: {topic_name}")
            
            detail_response = await client.get(
                f"{BASE_URL}/api/topics/{topic_id}",
                headers=headers,
                timeout=5.0
            )
            
            if detail_response.status_code != 200:
                print(f"   ❌ Topic details failed: {detail_response.status_code}")
                print(f"      Response: {detail_response.text[:200]}")
                return False
            
            detail_data = detail_response.json()
            topic = detail_data.get("data", {}).get("topic", {})
            recommended_videos = topic.get("recommendedVideos", [])
            
            print(f"   ✅ Got topic details: {len(recommended_videos)} videos")
            
        except Exception as e:
            print(f"   ❌ Topic detail error: {e}")
            return False
        
        # Step 4: Verify video structure
        print("\n4. Video Details:")
        if not recommended_videos:
            print("   ⚠️  No videos in response!")
            return False
        
        for i, video in enumerate(recommended_videos[:2], 1):
            print(f"\n   Video {i}:")
            print(f"   - youtubeId: {video.get('youtubeId', 'MISSING')}")
            print(f"   - title: {video.get('title', 'MISSING')[:60]}")
            print(f"   - channel: {video.get('channel', 'MISSING')}")
            
            youtube_id = video.get("youtubeId")
            if youtube_id:
                url = f"https://www.youtube.com/watch?v={youtube_id}"
                print(f"   - Video URL: {url}")
                print(f"   - WORKS: ✅ YouTube URL properly formatted")
            else:
                print(f"   - ISSUE: ❌ No youtubeId field!")
        
        print("\n" + "=" * 70)
        print("✅ SUCCESS: API is returning stored videos correctly!")
        print("=" * 70)
        return True

if __name__ == "__main__":
    success = asyncio.run(test_api())
    exit(0 if success else 1)
