#!/usr/bin/env python3
"""Fetch REAL YouTube videos and verify they are embeddable"""

import sys
sys.path.insert(0, ".")

import asyncio
from googleapiclient.discovery import build
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# Real topic-to-search-query mappings
SEARCH_QUERIES = {
    "Syntax & Variables": "Python syntax variables tutorial",
    "Data Types": "Python data types tutorial",
    "Control Structures": "Python if else while loop tutorial",
    "Functions": "Python functions tutorial",
    "OOP Concepts": "Python object oriented programming tutorial",
    "Modules & Packages": "Python modules packages tutorial",
    "File Handling": "Python file handling I/O tutorial",
    "Exception Handling": "Python exception handling tutorial",
    "Libraries (NumPy, Pandas)": "Python numpy pandas tutorial",
    "Web/AI Frameworks": "Python Django Flask AI tutorial",
    "Basics & Syntax": "JavaScript basics syntax tutorial",
    "DOM Manipulation": "JavaScript DOM tutorial",
    "Functions & Scope": "JavaScript functions scope tutorial",
    "Events Handling": "JavaScript events tutorial",
    "ES6+ Features": "JavaScript ES6 arrow functions tutorial",
    "Async Programming (Promises, Async/Await)": "JavaScript async await promises tutorial",
    "APIs & Fetch": "JavaScript fetch API tutorial",
    "Frameworks (React, Angular)": "React Angular tutorial",
    "Node.js Basics": "Node.js tutorial",
}

def get_search_query(topic_name):
    """Get search query for a topic"""
    for keyword, query in SEARCH_QUERIES.items():
        if keyword.lower() in topic_name.lower():
            return query
    # Default query from topic name
    return f"{topic_name} tutorial"

async def fetch_real_youtube_videos():
    print("\n" + "=" * 80)
    print("FETCHING REAL YOUTUBE VIDEOS - VERIFIED WORKING IDS")
    print("=" * 80)
    
    # Initialize YouTube API
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("ERROR: YOUTUBE_API_KEY not set!")
        return
    
    youtube = build("youtube", "v3", developerKey=api_key)
    
    # Connect to MongoDB
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
    client = MongoClient(mongo_url)
    db = client["pixel_pirates"]
    topics_collection = db["topics"]
    
    # Get all topics
    all_topics = list(topics_collection.find({}))
    print(f"\nFetching videos for {len(all_topics)} topics...\n")
    
    updated_count = 0
    failed_topics = []
    
    for i, topic in enumerate(all_topics, 1):
        topic_name = topic.get("name", "Unknown")
        topic_id = topic.get("_id")
        
        print(f"[{i:3d}/{len(all_topics)}] {topic_name}...", end=" ", flush=True)
        
        try:
            # Search for videos on YouTube
            search_query = get_search_query(topic_name)
            
            request = youtube.search().list(
                q=search_query,
                part="snippet",
                type="video",
                maxResults=5,
                videoEmbeddable="true",  # Only embeddable videos (must be string)
                order="relevance",
                safeSearch="strict",
                relevanceLanguage="en"
            )
            
            response = request.execute()
            videos = []
            
            # Process search results
            for item in response.get("items", [])[:3]:  # Get top 3 videos
                video_id = item["id"]["videoId"]
                snippet = item["snippet"]
                
                videos.append({
                    "youtubeId": video_id,
                    "title": snippet["title"],
                    "channel": snippet["channelTitle"],
                    "description": snippet["description"],
                    "views": 0,
                    "uploadedAt": snippet["publishedAt"],
                    "url": f"https://www.youtube.com/watch?v={video_id}"
                })
            
            if videos:
                # Update MongoDB
                topics_collection.update_one(
                    {"_id": topic_id},
                    {"$set": {"videos": videos}}
                )
                print(f"[OK] {len(videos)} videos")
                updated_count += 1
            else:
                print(f"[WARN] No videos found")
                failed_topics.append(topic_name)
                
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower():
                print(f"[QUOTA] YouTube API quota exceeded")
                print("\nTo enable more searches, enable billing on Google Cloud Console:")
                print("  https://console.cloud.google.com/billing")
                break
            else:
                print(f"[ERROR] {error_msg[:40]}")
                failed_topics.append(topic_name)
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total topics: {len(all_topics)}")
    print(f"Successfully updated: {updated_count}/{len(all_topics)}")
    
    if failed_topics:
        print(f"\nFailed topics ({len(failed_topics)}):")
        for topic in failed_topics[:5]:
            print(f"  - {topic}")
        if len(failed_topics) > 5:
            print(f"  ... and {len(failed_topics) - 5} more")
    
    print("\n[OK] Videos fetched from YouTube API!")
    print("Refresh frontend to see working videos.")
    print("\n" + "=" * 80 + "\n")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fetch_real_youtube_videos())
