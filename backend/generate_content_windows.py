#!/usr/bin/env python
"""
Complete Content Generation for 200 Topics
Windows-compatible, UTF-8 safe version

Generates:
- YouTube Videos (highly recommended using provided API key)
- 4 Types of Explanations (visual, simplified, logical, analogy using Gemini)
- Professional PDFs
- Mock Test Questions (8 per topic)
- Stores all in MongoDB

Run: python generate_content_windows.py
"""

import asyncio
import json
import os
import sys
import time
import io
from typing import List, Dict, Any
from pathlib import Path

# Force UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load environment variables early
from dotenv import load_dotenv
load_dotenv()

import httpx
import pymongo
from pymongo import MongoClient
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import colors

# Configure Gemini
try:
    import google.generativeai as genai
    GEMINI_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_KEY:
        genai.configure(api_key=GEMINI_KEY)
        GEMINI_MODEL = genai.GenerativeModel("gemini-2.5-flash")
    else:
        GEMINI_MODEL = None
except:
    GEMINI_MODEL = None

# Configuration
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "IzaSyA3_26DIrG1LvgJEAlhr05QXcB-tFks4Mc")
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
MONGODB_DB = os.getenv("MONGODB_DATABASE", "pixel_pirates")
PDF_DIR = Path("storage/pdfs")
PDF_DIR.mkdir(parents=True, exist_ok=True)

log = print  # Use standard print for logging


def log_header(text):
    log("")
    log("="*80)
    log(text)
    log("="*80)


def log_step(num, text):
    log(f"\n[{num}] {text}")


def log_success(text):
    log(f"    [OK] {text}")


def log_error(text):
    log(f"    [ERROR] {text}")


# ========== YOUTUBE VIDEO SEARCH ==========


async def search_youtube_videos(topic_name: str, language: str) -> List[Dict]:
    """Search YouTube for highly recommended videos"""
    try:
        search_query = f"{topic_name} {language} tutorial beginner"
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": search_query,
            "type": "video",
            "maxResults": 5,
            "order": "relevance",
            "videoEmbeddable": "true",
            "key": YOUTUBE_API_KEY,
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            
            if response.status_code != 200:
                log_error(f"YouTube API: {response.status_code}")
                return []
            
            data = response.json()
            videos = []
            
            for item in data.get("items", [])[:3]:
                video_id = item["id"].get("videoId")
                snippet = item["snippet"]
                
                videos.append({
                    "youtubeId": video_id,
                    "title": snippet.get("title", ""),
                    "description": snippet.get("description", "")[:200],
                    "thumbnail": snippet["thumbnails"].get("high", {}).get("url", ""),
                    "channel": snippet.get("channelTitle", ""),
                    "publishedAt": snippet.get("publishedAt", ""),
                })
            
            return videos
            
    except Exception as e:
        log_error(f"YouTube search: {str(e)[:100]}")
        return []


# ========== GENERATE EXPLANATIONS (4 TYPES) ==========


async def generate_explanations(topic_name: str, overview: str, difficulty: str) -> List[Dict]:
    """Generate 4 types of explanations using Gemini"""
    if not GEMINI_MODEL:
        log_error("Gemini API not configured")
        return []
    
    try:
        explanations = []
        
        prompts = {
            "visual": f"Provide VISUAL explanation for {topic_name} with ASCII diagrams or structure descriptions. Max 200 words.",
            "simplified": f"Provide SIMPLIFIED explanation for beginner using everyday language for {topic_name}. Max 200 words.",
            "logical": f"Provide LOGICAL step-by-step explanation for {topic_name}. Max 300 words.",
            "analogy": f"Provide ANALOGY-based explanation using metaphors for {topic_name}. Max 250 words.",
        }
        
        for style, prompt in prompts.items():
            try:
                response = await asyncio.to_thread(
                    GEMINI_MODEL.generate_content, prompt
                )
                explanations.append({
                    "style": style,
                    "title": f"{style.capitalize()}: {topic_name}",
                    "content": response.text[:2000],
                })
                await asyncio.sleep(1)  # Rate limiting
            except Exception as e:
                log_error(f"Explanation ({style}): {str(e)[:50]}")
        
        return explanations
        
    except Exception as e:
        log_error(f"Explanations: {str(e)[:100]}")
        return []


# ========== GENERATE MOCK QUESTIONS ==========


async def generate_mock_questions(topic_name: str, overview: str) -> List[Dict]:
    """Generate 8 mock test questions"""
    if not GEMINI_MODEL:
        return []
    
    try:
        prompt = f"""Generate exactly 8 multiple-choice questions for {topic_name}.
        Format as JSON array: [{{"question": "...", "options": ["A:...", "B:...", "C:...", "D:..."], "correctOption": 0, "explanation": "..."}}]"""
        
        response = await asyncio.to_thread(GEMINI_MODEL.generate_content, prompt)
        
        # Parse JSON
        text = response.text
        start = text.find('[')
        end = text.rfind(']') + 1
        if start >= 0 and end > start:
            json_str = text[start:end]
            questions = json.loads(json_str)
            return questions[:8]
        
        return []
        
    except Exception as e:
        log_error(f"Mock questions: {str(e)[:50]}")
        return []


# ========== GENERATE PDF ==========


async def generate_pdf(topic_name: str, overview: str, explanations: List[Dict], questions: List[Dict]) -> str:
    """Generate PDF study guide"""
    try:
        pdf_filename = f"{topic_name.replace(' ', '_').replace('/', '_')}.pdf"
        pdf_path = PDF_DIR / pdf_filename
        
        doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=30,
        )
        story.append(Paragraph(topic_name, title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Explanations
        story.append(Paragraph("Learn This Topic", styles['Heading2']))
        for exp in explanations[:2]:  # Include first 2 explanations
            story.append(Paragraph(exp.get('title', 'Explanation'), styles['Heading3']))
            content = exp.get('content', '')[:500]
            story.append(Paragraph(content, styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Mock questions header
        story.append(Paragraph("Practice Questions", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        
        # Build PDF
        try:
            doc.build(story)
            return str(pdf_path)
        except Exception as e:
            log_error(f"PDF build: {str(e)[:50]}")
            return ""
        
    except Exception as e:
        log_error(f"PDF generation: {str(e)[:100]}")
        return ""


# ========== MONGODB OPERATIONS ==========


def get_mongo_client():
    """Get MongoDB client"""
    try:
        client = MongoDB(MONGODB_URL)
        return client
    except:
        return None


class MongoDB:
    def __init__(self, url):
        self.client = MongoClient(url, serverSelectionTimeoutMS=5000)
        self.db = self.client[MONGODB_DB]
        self.topics = self.db.topics
        self.mock_tests = self.db.mockTests
    
    def get_all_topics(self) -> List[Dict]:
        return list(self.topics.find({}, {"_id": 1, "name": 1, "language": 1, "difficulty": 1, "overview": 1}))
    
    def update_topic(self, topic_id: str, videos: List, explanations: List, questions: List, pdf: str):
        """Update topic with generated content"""
        try:
            self.topics.update_one(
                {"_id": topic_id},
                {"$set": {
                    "videos": videos,
                    "explanations": explanations,
                    "pdf_path": pdf,
                    "generated_at": time.time(),
                }}
            )
            return True
        except:
            return False
    
    def save_mock_test(self, topic_id: str, questions: List):
        """Save mock test questions"""
        try:
            self.mock_tests.insert_one({
                "topic_id": topic_id,
                "questions": questions,
                "created_at": time.time(),
            })
            return True
        except:
            return False
    
    def close(self):
        self.client.close()


# ========== MAIN PROCESSING ==========


async def process_topic(db: MongoDB, topic: Dict, progress: Dict):
    """Process single topic"""
    try:
        topic_id = topic["_id"]
        topic_name = topic.get("name", "Unknown")
        language = topic.get("language", "")
        difficulty = topic.get("difficulty", "Intermediate")
        overview = topic.get("overview", "")
        
        log_step(1, f"Processing: {topic_name}")
        
        # YouTube videos
        videos = await search_youtube_videos(topic_name, language)
        log_success(f"Found {len(videos)} videos")
        
        # Explanations
        explanations = await generate_explanations(topic_name, overview, difficulty)
        log_success(f"Generated {len(explanations)} explanations")
        
        # Mock questions
        questions = await generate_mock_questions(topic_name, overview)
        log_success(f"Generated {len(questions)} questions")
        
        # PDF
        pdf_path = await generate_pdf(topic_name, overview, explanations, questions)
        if pdf_path:
            log_success(f"Generated PDF")
        
        # Save to MongoDB
        db.update_topic(topic_id, videos, explanations, questions, pdf_path)
        db.save_mock_test(topic_id, questions)
        
        progress["completed"] += 1
        log_success(f"Saved to MongoDB ({progress['completed']}/{progress['total']})")
        
        return True
        
    except Exception as e:
        progress["failed"] += 1
        log_error(f"Failed: {str(e)[:100]}")
        return False


async def main():
    """Main generation process"""
    log_header("PIXEL PIRATES - CONTENT GENERATION")
    log(f"Generating content for 200 topics...")
    log(f"  - YouTube videos (3+ per topic)")
    log(f"  - 4 explanation types (visual, simplified, logical, analogy)")
    log(f"  - PDF guides")
    log(f"  - Mock tests (8 questions per topic)")
    log("")
    
    # Connect to MongoDB
    db = MongoDB(MONGODB_URL)
    
    try:
        db.client.server_info()
        log_success("MongoDB connected")
    except:
        log_error("Cannot connect to MongoDB")
        return
    
    # Get topics
    topics = db.get_all_topics()
    log_success(f"Found {len(topics)} topics")
    
    if not topics:
        log_error("No topics in database")
        return
    
    progress = {"total": len(topics), "completed": 0, "failed": 0}
    
    # Process with concurrency limit (2 at a time)
    sem = asyncio.Semaphore(2)
    
    async def process_with_sem(topic):
        async with sem:
            await process_topic(db, topic, progress)
            await asyncio.sleep(2)  # Rate limiting
    
    # Process all topics
    tasks = [process_with_sem(topic) for topic in topics]
    await asyncio.gather(*tasks)
    
    # Final report
    log_header("GENERATION COMPLETE")
    log(f"Total: {progress['total']}")
    log(f"Completed: {progress['completed']}")
    log(f"Failed: {progress['failed']}")
    log(f"Success Rate: {100*progress['completed']//progress['total']}%")
    
    db.close()


if __name__ == "__main__":
    asyncio.run(main())
