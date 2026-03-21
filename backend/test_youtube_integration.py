#!/usr/bin/env python3
"""Test YouTube integration with topics API"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000/api"

def test_youtube_integration():
    """Test the YouTube video fetching for topics"""
    
    # First, authenticate
    print("🔐 Authenticating...")
    login_data = {
        "email": "test@example.com",
        "password": "test123"
    }
    
    # Try login first, if it fails, register
    login_resp = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if login_resp.status_code == 200:
        auth_result = login_resp.json()
        token = auth_result["data"].get("access_token", "")
        print(f"✅ Logged in, token: {token[:20]}...")
    elif login_resp.status_code in [400, 401, 404]:
        # Try register
        print("  Attempting to register new user...")
        reg_resp = requests.post(f"{BASE_URL}/auth/register", json=login_data)
        if reg_resp.status_code == 200:
            auth_result = reg_resp.json()
            token = auth_result["data"].get("access_token", "")
            print(f"✅ Registered, token: {token[:20]}...")
        else:
            print(f"❌ Registration failed: {reg_resp.status_code}")
            print(f"   Response: {reg_resp.text[:200]}")
            return
    else:
        print(f"❌ Authentication failed: {login_resp.status_code}")
        return
    
    # Get all topics
    print("\n📚 Fetching topics list...")
    headers = {"Authorization": f"Bearer {token}"}
    
    topics_resp = requests.get(f"{BASE_URL}/topics", headers=headers)
    if topics_resp.status_code == 200:
        topics_result = topics_resp.json()
        topics = topics_result["data"].get("topics", [])
        print(f"✅ Retrieved {len(topics)} topics")
        
        if topics:
            # Get first topic details
            first_topic_id = topics[0]["id"]
            topic_name = topics[0]["topicName"]
            print(f"\n🎯 Fetching details for: {topic_name} (ID: {first_topic_id})")
            
            topic_resp = requests.get(f"{BASE_URL}/topics/{first_topic_id}", headers=headers)
            if topic_resp.status_code == 200:
                topic_result = topic_resp.json()
                topic_data = topic_result["data"].get("topic", {})
                
                videos = topic_data.get("recommendedVideos", [])
                print(f"\n🎬 Videos returned: {len(videos)}")
                
                if videos:
                    for i, video in enumerate(videos[:3]):
                        print(f"\n  Video {i+1}:")
                        print(f"    Title: {video.get('title', 'N/A')[:60]}")
                        print(f"    YouTube ID: {video.get('youtubeId', 'N/A')}")
                        print(f"    Channel: {video.get('channelTitle', 'N/A')}")
                        print(f"    Views: {video.get('viewCount', 0):,}")
                else:
                    print("   ⚠️ No videos found!")
            else:
                print(f"❌ Topic fetch failed: {topic_resp.status_code}")
                print(f"   Response: {topic_resp.text[:500]}")
    else:
        print(f"❌ Topics list failed: {topics_resp.status_code}")
        print(f"   Response: {topics_resp.text[:200]}")

if __name__ == "__main__":
    print("🚀 Starting YouTube Integration Test\n")
    test_youtube_integration()
    print("\n✅ Test complete!")
