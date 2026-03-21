#!/usr/bin/env python3
"""Check video format in API response"""

import sys
sys.path.insert(0, ".")

import asyncio
import httpx
import json

async def check_video_format():
    print("\nCHECKING VIDEO FORMAT IN API RESPONSE\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Login
        login_resp = await client.post(
            "http://localhost:5000/api/auth/login",
            json={"email": "alex@edutwin.com", "password": "password123"}
        )
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get first topic with videos
        topics_resp = await client.get(
            "http://localhost:5000/api/topics",
            headers=headers
        )
        topics = topics_resp.json()["data"]["topics"]
        first_topic_id = topics[0]["id"]
        
        # Get topic details
        print(f"Fetching topic details for: {topics[0]['topicName']}\n")
        detail_resp = await client.get(
            f"http://localhost:5000/api/topics/{first_topic_id}",
            headers=headers
        )
        
        topic = detail_resp.json()["data"]["topic"]
        videos = topic.get("recommendedVideos", [])
        
        print("RAW API RESPONSE (first video):")
        print("=" * 80)
        print(json.dumps(videos[0] if videos else {}, indent=2))
        print("=" * 80)
        
        if videos:
            video = videos[0]
            print(f"\nVideo Fields Check:")
            print(f"  - youtubeId: {video.get('youtubeId', 'MISSING')}")
            print(f"  - title: {video.get('title', 'MISSING')}")
            print(f"  - channel: {video.get('channel', 'MISSING')}")
            print(f"  - viewCount: {video.get('viewCount', 'MISSING')}")
            
            if 'youtubeId' in video:
                print(f"\n[OK] youtubeId field present!")
                print(f"Video URL would be: https://www.youtube.com/watch?v={video['youtubeId']}")
            else:
                print(f"\n[ERROR] youtubeId field MISSING!")
                print("Available fields:", list(video.keys()))

if __name__ == "__main__":
    asyncio.run(check_video_format())
