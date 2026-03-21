#!/usr/bin/env python
"""
GENERATE ALL CONTENT - Using Gemini AI + YouTube API
Generates explanations, quiz questions, and videos for all 200 topics
"""

import os
import sys
import asyncio
import json
import httpx
from typing import List, Dict, Any
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")

print("=" * 80)
print("PIXEL PIRATES - GENERATE ALL CONTENT WITH AI")
print("=" * 80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Using: Gemini API + YouTube API + MongoDB")
print("=" * 80)

# ============================================================================
# GEMINI AI CONTENT GENERATION
# ============================================================================

class GeminiContentGenerator:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    
    async def generate(self, prompt: str) -> str:
        """Call Gemini API"""
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"{self.base_url}?key={self.api_key}",
                    json={
                        "contents": [
                            {"parts": [{"text": prompt}]}
                        ],
                        "generationConfig": {
                            "temperature": 0.7,
                            "maxOutputTokens": 2048
                        }
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "candidates" in data and len(data["candidates"]) > 0:
                        return data["candidates"][0]["content"]["parts"][0]["text"]
                return ""
        except Exception as e:
            print(f"  ❌ Gemini error: {e}")
            return ""
    
    async def generate_explanation(self, topic: str, style: str) -> str:
        """Generate explanation in style"""
        prompts = {
            "simplified": f"Explain '{topic}' in very simple language for beginners. Use real-world examples. Keep it under 300 words.",
            "logical": f"Provide a step-by-step logical explanation of '{topic}'. Explain the 'why' and 'how'. Under 300 words.",
            "visual": f"Describe '{topic}' in a way that could be visualized with diagrams. Include key visual elements. Under 300 words.",
            "analogy": f"Explain '{topic}' using real-world analogies and comparisons. Make it relatable and memorable. Under 300 words."
        }
        
        prompt = prompts.get(style, prompts["simplified"])
        result = await self.generate(prompt)
        return result.strip()
    
    async def generate_quiz(self, topic: str, count: int = 5) -> List[Dict]:
        """Generate quiz questions"""
        prompt = f"""Generate exactly {count} multiple-choice questions for '{topic}'.

Return ONLY valid JSON (no markdown, no extra text):
[
  {{"question": "What is...", "options": ["A) Answer1", "B) Answer2", "C) Answer3", "D) Answer4"], "correct": 0, "explanation": "Explanation..."}}
]"""
        
        text = await self.generate(prompt)
        try:
            # Extract JSON from response
            result = json.loads(text)
            return result[:count]
        except:
            return []
    
    async def generate_overview(self, topic: str) -> str:
        """Generate topic overview"""
        prompt = f"Write a concise (2-3 sentence) overview of '{topic}'. What is it and why is it important?"
        return await self.generate(prompt)

# ============================================================================
# YOUTUBE VIDEO FETCHING
# ============================================================================

class YouTubeVideoFetcher:
    def __init__(self):
        self.api_key = YOUTUBE_API_KEY
        self.base_url = "https://www.googleapis.com/youtube/v3/search"
    
    async def search(self, topic: str, max_results: int = 3) -> List[Dict]:
        """Search YouTube for videos"""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(
                    self.base_url,
                    params={
                        "q": f"{topic} tutorial",
                        "part": "snippet",
                        "type": "video",
                        "maxResults": max_results,
                        "order": "relevance",
                        "videoCategoryId": "27",  # Education category
                        "key": self.api_key
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    videos = []
                    
                    for item in data.get("items", []):
                        video = {
                            "youtubeId": item["id"]["videoId"],
                            "title": item["snippet"]["title"],
                            "description": item["snippet"]["description"][:200],
                            "channel": item["snippet"]["channelTitle"],
                            "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"]
                        }
                        videos.append(video)
                    
                    return videos
                return []
        except Exception as e:
            print(f"  ❌ YouTube error: {e}")
            return []

# ============================================================================
# MONGODB OPERATIONS
# ============================================================================

async def connect_mongodb():
    """Connect to MongoDB"""
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient(MONGODB_URL)
        db = client['pixel_pirates']
        await db.command('ping')
        print(f"✅ Connected to MongoDB")
        return db
    except Exception as e:
        print(f"❌ MongoDB error: {e}")
        return None

async def generate_topic_content(db, topic_id: str, topic_name: str, gemini: GeminiContentGenerator, youtube: YouTubeVideoFetcher):
    """Generate all content for a topic"""
    try:
        print(f"\n  📝 {topic_name}...")
        
        # Generate overview
        overview = await gemini.generate_overview(topic_name)
        
        # Generate explanations
        explanations = {}
        for style in ["simplified", "logical", "visual", "analogy"]:
            content = await gemini.generate_explanation(topic_name, style)
            if content:
                explanations[style] = content
        
        # Generate quiz
        quiz = await gemini.generate_quiz(topic_name, count=5)
        
        # Fetch videos
        videos = await youtube.search(topic_name, max_results=3)
        
        # Prepare update
        update_data = {
            "overview": overview,
            "explanations": explanations,
            "quizzes": quiz,
            "recommendedVideos": videos,
            "generatedAt": datetime.now().isoformat()
        }
        
        # Update in MongoDB
        if db:
            result = await db.topics.update_one(
                {"_id": topic_id},
                {"$set": update_data}
            )
            
            status = "✅" if result.modified_count > 0 else "⚠️"
            print(f"    {status} Generated: overview, {len(explanations)} explanations, {len(quiz)} quiz, {len(videos)} videos")
            return True
        return False
        
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return False

# ============================================================================
# MAIN
# ============================================================================

async def main():
    # Initialize
    db = await connect_mongodb()
    if not db:
        print("❌ Cannot connect to MongoDB. Please ensure MongoDB is running.")
        sys.exit(1)
    
    gemini = GeminiContentGenerator()
    youtube = YouTubeVideoFetcher()
    
    # Get all topics
    try:
        cursor = db.topics.find({}).limit(5)  # Test with 5 first
        topics = await cursor.to_list(length=None)
    except Exception as e:
        print(f"❌ Error fetching topics: {e}")
        return
    
    print(f"\n📚 Found {len(topics)} topics")
    print("=" * 80)
    print("GENERATING CONTENT FOR ALL TOPICS")
    print("=" * 80)
    
    successful = 0
    failed = 0
    
    for i, topic in enumerate(topics, 1):
        print(f"\n[{i}/{len(topics)}]", end="")
        
        topic_id = topic.get("_id")
        topic_name = topic.get("topicName", "Unknown")
        
        success = await generate_topic_content(db, topic_id, topic_name, gemini, youtube)
        if success:
            successful += 1
        else:
            failed += 1
        
        # Rate limit: wait between requests
        if i < len(topics):
            await asyncio.sleep(1)
    
    # Summary
    print("\n" + "=" * 80)
    print("GENERATION COMPLETE")
    print("=" * 80)
    print(f"✅ Successful: {successful}/{len(topics)}")
    print(f"❌ Failed: {failed}/{len(topics)}")
    print(f"\n✓ All content generated and stored in MongoDB")
    print(f"✓ Frontend will now display AI-generated content and YouTube videos")

if __name__ == "__main__":
    asyncio.run(main())
