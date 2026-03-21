#!/usr/bin/env python3
"""Direct YouTube API test with minimal request"""

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("YOUTUBE_API_KEY")
print(f"Testing YouTube API with key: {api_key[:20]}...")

try:
    youtube = build("youtube", "v3", developerKey=api_key)
    
    # Simple search
    request = youtube.search().list(
        q="Python tutorial",
        part="snippet",
        maxResults=1,
        type="video"
    )
    response = request.execute()
    
    if response.get("items"):
        print(f"SUCCESS! Found video: {response['items'][0]['snippet']['title']}")
    else:
        print("No videos found (search returned empty)")
        
except HttpError as e:
    print(f"YouTube API Error: {e}")
    error_content = str(e)
    if "quotaExceeded" in error_content:
        print("\nThis API key has exceeded quota limits")
    elif "forbidden" in error_content.lower():
        print("\nForbidden - API might not be enabled for this key")
    elif "disabled" in error_content.lower():
        print("\nAPI is disabled on this key")
        
except Exception as e:
    print(f"Unexpected error: {e}")
