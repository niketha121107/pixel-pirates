#!/usr/bin/env python3
"""Debug: Check what the API is actually returning"""

import sys
sys.path.insert(0, ".")

import asyncio
import httpx
import json

async def debug_api_response():
    print("\nDEBUGGING API RESPONSE\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Login
        login_resp = await client.post(
            "http://localhost:5000/api/auth/login",
            json={"email": "alex@edutwin.com", "password": "password123"}
        )
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get all topics
        topics_resp = await client.get(
            "http://localhost:5000/api/topics",
            headers=headers
        )
        topics = topics_resp.json()["data"]["topics"]
        first_topic_id = topics[0]["id"]
        
        # Get topic details
        print(f"Fetching: {topics[0]['topicName']}\n")
        detail_resp = await client.get(
            f"http://localhost:5000/api/topics/{first_topic_id}",
            headers=headers
        )
        
        full_response = detail_resp.json()
        topic = full_response["data"]["topic"]
        
        print("FULL API RESPONSE:")
        print("=" * 80)
        # Print all top-level keys
        print(f"Topic keys: {list(topic.keys())}\n")
        
        # Check for various video field names
        print("Video field check:")
        print(f"  - topic.videos: {topic.get('videos', 'NOT FOUND')}")
        print(f"  - topic.recommendedVideos: {topic.get('recommendedVideos', 'NOT FOUND')}")
        print(f"  - topic.videoUrl: {topic.get('videoUrl', 'NOT FOUND')}")
        
        print("\n" + "=" * 80)
        print("FIRST VIDEO DETAILS:")
        print("=" * 80)
        
        videos = topic.get("recommendedVideos") or topic.get("videos") or []
        if videos:
            print(json.dumps(videos[0], indent=2))
        else:
            print("NO VIDEOS FOUND!")
            print("\nAll topic data:")
            print(json.dumps(topic, indent=2)[:1000])

if __name__ == "__main__":
    asyncio.run(debug_api_response())
