#!/usr/bin/env python3
"""Verify all stored videos are available and accessible via API"""

import sys
sys.path.insert(0, ".")

import asyncio
import httpx

async def verify_stored_videos():
    print("\n" + "=" * 80)
    print("STORED VIDEOS VERIFICATION")
    print("=" * 80)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Login
        print("\n1. Authenticating...")
        login_resp = await client.post(
            "http://localhost:5000/api/auth/login",
            json={"email": "alex@edutwin.com", "password": "password123"}
        )
        if login_resp.status_code != 200:
            print(f"   FAILED to login: {login_resp.status_code}")
            return
        
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("   [OK] Login successful")
        
        # Get all topics
        print("\n2. Fetching all topics...")
        topics_resp = await client.get(
            "http://localhost:5000/api/topics",
            headers=headers
        )
        if topics_resp.status_code != 200:
            print(f"   FAILED: {topics_resp.status_code}")
            return
        
        topics = topics_resp.json()["data"]["topics"]
        print(f"   [OK] Found {len(topics)} topics")
        
        # Check stored videos for each topic
        print("\n3. Checking stored videos for each topic...")
        topics_with_videos = 0
        total_videos = 0
        topics_without_videos = []
        
        for i, topic_summary in enumerate(topics, 1):
            topic_id = topic_summary["id"]
            topic_name = topic_summary["topicName"]
            
            # Get topic details (includes videos)
            detail_resp = await client.get(
                f"http://localhost:5000/api/topics/{topic_id}",
                headers=headers,
                timeout=10.0
            )
            
            if detail_resp.status_code != 200:
                print(f"   [{i:3d}] ❌ {topic_name}: ERROR {detail_resp.status_code}")
                topics_without_videos.append(topic_name)
                continue
            
            topic = detail_resp.json()["data"]["topic"]
            videos = topic.get("recommendedVideos", [])
            
            if videos:
                topics_with_videos += 1
                total_videos += len(videos)
                video_titles = [v.get("title", "Unknown")[:40] for v in videos[:2]]
                print(f"   [{i:3d}] [OK] {topic_name}: {len(videos)} videos")
                for j, video in enumerate(videos, 1):
                    video_id = video.get("youtubeId", "N/A")
                    title = video.get("title", "Unknown")[:50]
                    print(f"         {j}. {title} (ID: {video_id})")
            else:
                print(f"   [{i:3d}] [WARN] {topic_name}: NO VIDEOS")
                topics_without_videos.append(topic_name)
            
            # Show progress every 50 topics
            if i % 50 == 0:
                print(f"      ... processed {i}/{len(topics)} topics ...")
        
        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total topics: {len(topics)}")
        print(f"Topics with stored videos: {topics_with_videos}/{len(topics)}")
        print(f"Total stored videos: {total_videos}")
        print(f"Average videos per topic: {total_videos / max(1, topics_with_videos):.1f}")
        
        if topics_without_videos:
            print(f"\n[WARN] Topics WITHOUT videos ({len(topics_without_videos)}):")
            for name in topics_without_videos[:10]:
                print(f"   - {name}")
            if len(topics_without_videos) > 10:
                print(f"   ... and {len(topics_without_videos) - 10} more")
        
        if topics_with_videos == len(topics):
            print("\n[OK] ALL TOPICS HAVE STORED VIDEOS!")
            print("The frontend should display all videos correctly.")
        else:
            print(f"\n[WARN] {len(topics_without_videos)} topics missing videos")
            print("You may need to regenerate videos for these topics.")
    
    print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    asyncio.run(verify_stored_videos())
