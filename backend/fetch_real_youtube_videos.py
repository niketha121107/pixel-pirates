#!/usr/bin/env python3
"""Fetch REAL YouTube videos for all topics and update database"""

import sys
sys.path.insert(0, ".")

import asyncio
from app.services.youtube_service import youtube_service
from app.data import get_all_topics, update_topic_videos
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

async def fetch_and_update_real_videos():
    print("\n" + "=" * 80)
    print("FETCHING REAL YOUTUBE VIDEOS FROM API")
    print("=" * 80)
    
    # Connect to MongoDB
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
    client = MongoClient(mongo_url)
    db = client["pixel_pirates"]
    topics_collection = db["topics"]
    
    # Get all topics
    topics = get_all_topics()
    print(f"\nProcessing {len(topics)} topics...\n")
    
    updated_count = 0
    failed_count = 0
    
    for i, topic in enumerate(topics, 1):
        topic_id = str(topic.get("_id"))
        topic_name = topic.get("name", "Unknown")
        
        try:
            print(f"[{i:3d}/{len(topics)}] {topic_name}...", end=" ", flush=True)
            
            # Fetch real videos from YouTube API
            videos = await youtube_service.search_for_topic(
                topic_name=topic_name,
                language=topic.get("language", ""),
                max_results=3
            )
            
            if videos:
                # Update MongoDB with real video IDs
                topics_collection.update_one(
                    {"_id": topic.get("_id")},
                    {"$set": {"videos": videos}}
                )
                print(f"[OK] {len(videos)} videos")
                updated_count += 1
            else:
                print(f"[WARN] No videos found")
                failed_count += 1
                
        except Exception as e:
            print(f"[ERROR] {str(e)[:50]}")
            failed_count += 1
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total topics: {len(topics)}")
    print(f"Successfully updated: {updated_count}")
    print(f"Failed: {failed_count}")
    print(f"Updates: {updated_count}/{len(topics)}")
    
    if updated_count > 0:
        print("\n[OK] Real YouTube videos have been fetched and stored!")
        print("Refresh the frontend to see the updated videos.")
    else:
        print("\n[WARN] No videos were updated. This might be due to YouTube API quota.")
        print("Make sure billing is enabled on Google Cloud Console.")
    
    client.close()
    print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    asyncio.run(fetch_and_update_real_videos())
