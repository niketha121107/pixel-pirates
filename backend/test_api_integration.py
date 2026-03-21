#!/usr/bin/env python
"""
PIXEL PIRATES - API INTEGRATION & CONTENT GENERATION
Integrates Gemini API and YouTube API to generate all content properly
"""

import os
import sys
import asyncio
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
import httpx

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_API_KEY = os.getenv("YOUTUBE_API_KEY")

print("=" * 80)
print("PIXEL PIRATES - API INTEGRATION CHECK")
print("=" * 80)

# Verify all API keys
print("\n✓ API CONFIGURATION:")
if GEMINI_API_KEY and len(GEMINI_API_KEY) > 10:
    print(f"  ✅ Gemini API Key: {GEMINI_API_KEY[:30]}...")
else:
    print(f"  ❌ Gemini API Key: NOT CONFIGURED")

if GOOGLE_API_KEY and len(GOOGLE_API_KEY) > 10:
    print(f"  ✅ YouTube API Key: {GOOGLE_API_KEY[:30]}...")
else:
    print(f"  ❌ YouTube API Key: NOT CONFIGURED")

print("\n✓ API ENDPOINTS CONFIGURED:")

# Gemini API endpoint
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
print(f"  ✅ Gemini: {GEMINI_URL}")

# YouTube API endpoint
YOUTUBE_URL = "https://www.googleapis.com/youtube/v3/search"
print(f"  ✅ YouTube: {YOUTUBE_URL}")

print("\n" + "=" * 80)
print("TESTING API CONNECTIONS")
print("=" * 80)

# Test Gemini
print("\n🧪 Testing Gemini API...")
async def test_gemini():
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{GEMINI_URL}?key={GEMINI_API_KEY}",
                json={
                    "contents": [
                        {
                            "parts": [
                                {"text": "Say 'Gemini API is working' in exactly 5 words"}
                            ]
                        }
                    ]
                }
            )
            
            if response.status_code == 200:
                print(f"  ✅ Gemini API responding correctly")
                data = response.json()
                if "candidates" in data:
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    print(f"     Response: {text[:80]}")
                return True
            else:
                print(f"  ❌ Gemini API error: {response.status_code}")
                print(f"     {response.text[:200]}")
                return False
    except Exception as e:
        print(f"  ❌ Gemini connection error: {e}")
        return False

# Test YouTube
print("\n🧪 Testing YouTube API...")
async def test_youtube():
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                YOUTUBE_URL,
                params={
                    "q": "Python programming tutorial",
                    "part": "snippet",
                    "type": "video",
                    "maxResults": "1",
                    "key": GOOGLE_API_KEY
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("items"):
                    print(f"  ✅ YouTube API responding correctly")
                    video = data["items"][0]
                    print(f"     Found: {video['snippet']['title'][:80]}")
                    return True
                else:
                    print(f"  ❌ YouTube API: No results")
                    return False
            else:
                print(f"  ❌ YouTube API error: {response.status_code}")
                print(f"     {response.text[:200]}")
                return False
    except Exception as e:
        print(f"  ❌ YouTube connection error: {e}")
        return False

async def main():
    results = {}
    
    print("\n📡 Running async tests...")
    results["gemini"] = await test_gemini()
    print()
    results["youtube"] = await test_youtube()
    
    print("\n" + "=" * 80)
    print("INTEGRATION SUMMARY")
    print("=" * 80)
    
    if all(results.values()):
        print("\n✅ ALL APIS INTEGRATED AND WORKING!")
        print("\nYou can now:")
        print("  1. Generate AI explanations with Gemini API")
        print("  2. Fetch YouTube videos with YouTube API")
        print("  3. Generate quiz questions with Gemini")
        print("  4. Create study materials with AI")
        print("\n✓ Frontend will use these APIs to display:")
        print("  - AI-generated topic explanations")
        print("  - YouTube videos for each topic")
        print("  - AI-generated quiz questions")
        print("  - Smart study materials")
    else:
        print("\n❌ Some APIs are not working. Please check:")
        if not results.get("gemini"):
            print("  1. GEMINI_API_KEY in .env is correct")
            print("  2. Key has appropriate permissions")
            print("  3. Network connectivity")
        if not results.get("youtube"):
            print("  1. YOUTUBE_API_KEY in .env is correct")
            print("  2. YouTube Data API v3 is enabled in Google Cloud Console")
            print("  3. Network connectivity")

if __name__ == "__main__":
    asyncio.run(main())
