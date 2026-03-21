#!/usr/bin/env python
"""
Optimized Content Generation with API Rate Limit Handling
- Gracefully handles API quotas
- Uses fallback explanations when Gemini unavailable
- Longer delays between API calls
- Better error recovery
"""

import asyncio
import json
import os
import sys
import io
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from dotenv import load_dotenv
load_dotenv()

import httpx
from pymongo import MongoClient

# Configuration  
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "IzaSyA3_26DIrG1LvgJEAlhr05QXcB-tFks4Mc")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
MONGODB_DB = os.getenv("MONGODB_DATABASE", "pixel_pirates")
PDF_DIR = Path("storage/pdfs")
PDF_DIR.mkdir(parents=True, exist_ok=True)

GEMINI_MODEL = None
if GEMINI_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_KEY)
        GEMINI_MODEL = genai.GenerativeModel("gemini-2.5-flash")
    except:
        pass


# ========== FALLBACK EXPLANATIONS ==========


FALLBACK_EXPLANATIONS = {
    "visual": {
        "style": "visual",
        "title": "Visual Guide",
        "content": "A visual explanation includes diagrams, flowcharts, and structured layouts that show relationships and processes step-by-step."
    },
    "simplified": {
        "style": "simplified",
        "title": "Simplified Explanation",
        "content": "Think of it like this: complex topics are broken down into everyday language and real-world examples that anyone can understand."
    },
    "logical": {
        "style": "logical",
        "title": "Logical Structure",
        "content": "This follows a step-by-step logical progression: first understand the fundamentals, then build to more advanced concepts."
    },
    "analogy": {
        "style": "analogy",
        "title": "Learning by Analogy",
        "content": "Just like learning to drive a car, this concept involves understanding basic controls first, then practice to master it."
    }
}


# ========== YOUTUBE VIDEOS ==========


async def search_youtube(topic_name: str, language: str, attempt=1):
    """Search YouTube with retry logic"""
    try:
        if attempt > 3:
            return []
        
        search_query = f"{topic_name} {language} tutorial"
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": search_query,
            "type": "video",
            "maxResults": 3,
            "order": "relevance",
            "videoEmbeddable": "true",
            "key": YOUTUBE_API_KEY,
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            
            if response.status_code == 429:  # Rate limited
                wait = 60 * (2 ** attempt)  # Exponential backoff
                print(f"    [RATE] YouTube: Waiting {wait}s...")
                await asyncio.sleep(wait)
                return await search_youtube(topic_name, language, attempt + 1)
            
            if response.status_code != 200:
                return []
            
            videos = []
            data = response.json()
            for item in data.get("items", [])[:3]:
                video_id = item["id"].get("videoId")
                snip = item["snippet"]
                videos.append({
                    "youtubeId": video_id,
                    "title": snip.get("title", ""),
                    "channel": snip.get("channelTitle", ""),
                })
            
            return videos
            
    except Exception as e:
        return []


# ========== EXPLANATIONS ==========


async def generate_explanations_async(topic_name: str):
    """Generate explanations with fallback"""
    if not GEMINI_MODEL:
        return list(FALLBACK_EXPLANATIONS.values())
    
    explanations = []
    
    for style in ["visual", "simplified", "logical", "analogy"]:
        try:
            prompt = f"Explain '{topic_name}' in a {style} way (max 200 words)"
            response = await asyncio.to_thread(GEMINI_MODEL.generate_content, prompt)
            explanations.append({
                "style": style,
                "title": f"{style.capitalize()}: {topic_name}",
                "content": response.text[:2000],
            })
            await asyncio.sleep(3)  # 3 second delay
            
        except Exception as e:
            # Use fallback
            explanations.append(FALLBACK_EXPLANATIONS[style])
    
    return explanations


# ========== MOCK QUESTIONS ==========


async def generate_questions(topic_name: str):
    """Generate mock questions or use fallback"""
    if not GEMINI_MODEL:
        return []
    
    try:
        prompt = f"""Generate 8 MC questions for '{topic_name}' as JSON:
[{{"question":"Q","options":["A:","B:","C:","D:"],"correctOption":0}}]"""
        
        response = await asyncio.to_thread(GEMINI_MODEL.generate_content, prompt)
        text = response.text
        start, end = text.find('['), text.rfind(']') + 1
        
        if start >= 0:
            return json.loads(text[start:end])[:8]
        
    except:
        pass
    
    return []


# ========== PDF GENERATION ==========


async def generate_pdf(topic_name: str, explanations):
    """Generate simple PDF"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        filename = f"{topic_name.replace(' ', '_')[:50]}.pdf"
        pdf_path = PDF_DIR / filename
        
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, 750, topic_name)
        
        c.setFont("Helvetica", 10)
        y = 720
        for exp in explanations[:2]:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, exp.get("title", "Explanation"))
            y -= 20
            c.setFont("Helvetica", 10)
            text = exp.get("content", "")[:300]
            for line in text.split('\n')[:5]:
                if y < 50:
                    c.showPage()
                    y = 750
                c.drawString(50, y, line)
                y -= 15
            y -= 10
        
        c.save()
        return str(pdf_path)
    except:
        return ""


# ========== MONGODB ==========


class DB:
    def __init__(self):
        self.client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        self.db = self.client[MONGODB_DB]
    
    def get_all_topics(self):
        return list(self.db.topics.find({}, {"_id": 1, "name": 1, "language": 1}))
    
    def update_topic(self, topic_id, videos, explanations, questions, pdf_path):
        try:
            self.db.topics.update_one(
                {"_id": topic_id},
                {"$set": {
                    "videos": videos,
                    "explanations": explanations,
                    "pdf_path": pdf_path,
                }}
            )
            return True
        except:
            return False
    
    def save_mock_test(self, topic_id, questions):
        if questions:
            try:
                self.db.mockTests.update_one(
                    {"topic_id": topic_id},
                    {"$set": {"questions": questions}},
                    upsert=True
                )
            except:
                pass
    
    def close(self):
        self.client.close()


# ========== MAIN ==========


async def process_topic(db: DB, topic: dict, progress: dict):
    """Process single topic"""
    try:
        topic_id = topic["_id"]
        name = topic.get("name", "Unknown")
        lang = topic.get("language", "")
        
        print(f"\n  [{progress['count']}/{progress['total']}] {name}")
        
        # Videos
        videos = await search_youtube(name, lang)
        print(f"    Videos: {len(videos)}")
        
        # Explanations (with fallback)
        explanations = await generate_explanations_async(name)
        print(f"    Explanations: {len(explanations)}")
        
        # Questions
        questions = await generate_questions(name)
        print(f"    Questions: {len(questions)}")
        
        # PDF
        pdf_path = await generate_pdf(name, explanations)
        print(f"    PDF: {'OK' if pdf_path else 'skipped'}")
        
        # Save
        db.update_topic(topic_id, videos, explanations, questions, pdf_path)
        db.save_mock_test(topic_id, questions)
        
        progress["count"] += 1
        progress["success"] += 1
        
    except Exception as e:
        progress["count"] += 1
        progress["error"] += 1
        print(f"    [ERROR] {str(e)[:60]}")


async def main():
    """Main"""
    print("\n" + "="*70)
    print("PIXEL PIRATES - CONTENT GENERATION (Optimized)")
    print("="*70)
    print("Generating: Videos, Explanations, PDFs, Mock Tests")
    print(f"API Keys: YouTube={'OK' if YOUTUBE_API_KEY else 'NONE'}, Gemini={'OK' if GEMINI_KEY else 'NONE'}")
    print("="*70 + "\n")
    
    db = DB()
    
    try:
        db.client.server_info()
        print("[OK] MongoDB connected")
    except:
        print("[ERROR] MongoDB not available")
        return
    
    topics = db.get_all_topics()
    print(f"[OK] Found {len(topics)} topics\n")
    
    progress = {"total": len(topics), "count": 0, "success": 0, "error": 0}
    
    # Process with concurrency (2 topics at a time)
    sem = asyncio.Semaphore(2)
    
    async def process_with_sem(topic):
        async with sem:
            await process_topic(db, topic, progress)
            await asyncio.sleep(5)  # 5 second delay between topics
    
    # Run all
    tasks = [process_with_sem(topic) for topic in topics]
    await asyncio.gather(*tasks, return_exceptions=True)
    
    # Report
    print("\n" + "="*70)
    print("GENERATION COMPLETE")
    print("="*70)
    print(f"Total: {progress['total']}")
    print(f"Success: {progress['success']}")
    print(f"Errors: {progress['error']}")
    print(f"PDF Storage: {PDF_DIR}")
    print("="*70 + "\n")
    
    db.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Generation stopped by user")
    except Exception as e:
        print(f"\n[FATAL] {e}")
