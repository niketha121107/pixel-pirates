#!/usr/bin/env python
"""Test video playback URL generation"""
import requests
import json

API_URL = "http://localhost:5000/api/topics/1"

try:
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        print("\n✅ API Response received")
        print(f"Topic: {data.get('topicName', 'Unknown')}")
        print(f"\nRecommended Videos: {len(data.get('recommendedVideos', []))} found\n")
        
        for i, video in enumerate(data.get('recommendedVideos', [])[:3], 1):
            youtube_id = video.get('youtubeId', '')
            title = video.get('title', 'No title')
            url = f"https://www.youtube.com/watch?v={youtube_id}" if youtube_id else "INVALID"
            
            print(f"Video {i}:")
            print(f"  Title: {title}")
            print(f"  YouTube ID: {youtube_id}")
            print(f"  Embed URL: https://www.youtube.com/embed/{youtube_id}")
            print(f"  Watch URL: {url}")
            print()
    else:
        print(f"❌ API Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ Connection error: {e}")
    print("\nMake sure the backend is running on port 5000")
