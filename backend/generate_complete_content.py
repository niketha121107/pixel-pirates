"""
Complete Content Generation for 200 Topics
Generates: YouTube Videos, Explanations (4 types), PDFs, Mock Tests

Requirements:
- YouTube API Key (provided)
- Gemini API Key
- MongoDB connection
- ReportLab for PDF generation

Run: python generate_complete_content.py

YouTube API Key: IzaSyA3_26DIrG1LvgJEAlhr05QXcB-tFks4Mc
"""

import asyncio
import json
import os
import sys
import time
import traceback
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

import httpx
import pymongo
import google.generativeai as genai
from pymongo import MongoClient
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
import asyncio
from concurrent.futures import ThreadPoolExecutor

# ── Configuration ────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
YOUTUBE_API_KEY = "IzaSyA3_26DIrG1LvgJEAlhr05QXcB-tFks4Mc"  # Provided key
MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGODB_DATABASE", "pixel_pirates")

# Validate API keys
if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY not set. Add it to .env file.")
    sys.exit(1)

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
GEMINI_MODEL = genai.GenerativeModel("gemini-2.5-flash")

# Create storage directory for PDFs
PDF_STORAGE_DIR = Path("storage/pdfs")
PDF_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

print(f"✅ PDF Storage: {PDF_STORAGE_DIR.absolute()}")
print(f"✅ Using YouTube API Key: {YOUTUBE_API_KEY[:20]}...")
print(f"✅ Using Gemini Model: gemini-2.5-flash")


# ── YouTube Video Search ─────────────────────────────────────────
async def search_youtube_videos(topic_name: str, language: str) -> List[Dict[str, Any]]:
    """
    Search highly recommended YouTube videos related to topic.
    Returns list of videos with title, URL, duration, thumbnail.
    """
    try:
        # Build search query
        search_query = f"{topic_name} {language} tutorial beginner"
        
        # YouTube Data API endpoint
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
                print(f"⚠️  YouTube API error for '{topic_name}': {response.text}")
                return []
            
            data = response.json()
            videos = []
            
            for item in data.get("items", [])[:3]:  # Top 3 results
                video_id = item["id"].get("videoId")
                snippet = item["snippet"]
                
                videos.append({
                    "youtubeId": video_id,
                    "title": snippet.get("title", ""),
                    "description": snippet.get("description", "")[:200],
                    "thumbnail": snippet["thumbnails"].get("high", {}).get("url", ""),
                    "channel": snippet.get("channelTitle", ""),
                    "publishedAt": snippet.get("publishedAt", ""),
                    "language": language,
                })
            
            return videos
            
    except Exception as e:
        print(f"❌ Error searching YouTube for '{topic_name}': {e}")
        return []


# ── Generate Explanations (4 Types) ──────────────────────────────
async def generate_explanations(topic_name: str, overview: str, difficulty: str) -> List[Dict[str, str]]:
    """
    Generate 4 types of explanations for the topic using Gemini.
    Types: visual, simplified, logical, analogy
    """
    try:
        explanations = []
        
        # 1. Visual Explanation
        prompt_visual = f"""
        Topic: {topic_name}
        Difficulty: {difficulty}
        Overview: {overview}
        
        Generate a VISUAL explanation that uses:
        - ASCII diagrams or structure descriptions
        - Flow descriptions
        - Visual metaphors
        - Step-by-step visual breakdown
        
        Format as a clear, diagram-oriented explanation with ASCII art if possible.
        Keep it to 200-300 words.
        """
        
        response = await asyncio.to_thread(
            GEMINI_MODEL.generate_content, prompt_visual
        )
        explanations.append({
            "style": "visual",
            "title": f"Visual Guide to {topic_name}",
            "content": response.text[:2000],
            "icon": "📊"
        })
        
        # 2. Simplified Explanation
        prompt_simple = f"""
        Topic: {topic_name}
        Difficulty: {difficulty}
        
        Generate a SIMPLIFIED explanation for a beginner that:
        - Uses everyday language
        - Avoids jargon
        - Gives real-world examples
        - Breaks down complex concepts into bite-sized pieces
        
        Keep it under 250 words.
        """
        
        response = await asyncio.to_thread(
            GEMINI_MODEL.generate_content, prompt_simple
        )
        explanations.append({
            "style": "simplified",
            "title": f"Simple Explanation: {topic_name}",
            "content": response.text[:2000],
            "icon": "🎯"
        })
        
        # 3. Logical Explanation
        prompt_logical = f"""
        Topic: {topic_name}
        Difficulty: {difficulty}
        Overview: {overview}
        
        Generate a LOGICAL explanation that:
        - Uses step-by-step progression
        - Explains cause and effect
        - Uses logical structure (if-then relationships)
        - Builds from fundamentals to advanced concepts
        - Includes reasoning and why things work this way
        
        Keep it under 300 words.
        """
        
        response = await asyncio.to_thread(
            GEMINI_MODEL.generate_content, prompt_logical
        )
        explanations.append({
            "style": "logical",
            "title": f"Logical Structure: {topic_name}",
            "content": response.text[:2000],
            "icon": "🧠"
        })
        
        # 4. Analogy Explanation
        prompt_analogy = f"""
        Topic: {topic_name}
        Difficulty: {difficulty}
        Overview: {overview}
        
        Generate an ANALOGY-based explanation that:
        - Uses metaphors from everyday life
        - Compares to familiar concepts
        - Uses stories or scenarios
        - Makes abstract concepts concrete
        - Uses relatable examples
        
        Keep it under 250 words.
        """
        
        response = await asyncio.to_thread(
            GEMINI_MODEL.generate_content, prompt_analogy
        )
        explanations.append({
            "style": "analogy",
            "title": f"Learning by Analogy: {topic_name}",
            "content": response.text[:2000],
            "icon": "🎭"
        })
        
        return explanations
        
    except Exception as e:
        print(f"❌ Error generating explanations for '{topic_name}': {e}")
        return []


# ── Generate Mock Questions ──────────────────────────────────────
async def generate_mock_questions(topic_name: str, overview: str) -> List[Dict[str, Any]]:
    """
    Generate 5-10 mock test questions for the topic.
    Returns MCQ format with options and correct answer.
    """
    try:
        prompt = f"""
        Topic: {topic_name}
        Overview: {overview}
        
        Generate exactly 8 multiple-choice questions for a mock test about this topic.
        
        For each question, provide:
        1. The question text
        2. Four options (A, B, C, D)
        3. The correct option number (0-3)
        4. A brief explanation of why it's correct
        
        Format as JSON array:
        [
            {{
                "question": "...",
                "options": ["A: ...", "B: ...", "C: ...", "D: ..."],
                "correctOption": 0,
                "explanation": "..."
            }},
            ...
        ]
        
        Make questions progressively harder and cover different aspects of the topic.
        """
        
        response = await asyncio.to_thread(
            GEMINI_MODEL.generate_content, prompt
        )
        
        # Parse JSON response
        text = response.text
        # Extract JSON array
        start = text.find('[')
        end = text.rfind(']') + 1
        if start != -1 and end > start:
            json_str = text[start:end]
            questions = json.loads(json_str)
            
            # Ensure proper structure
            for q in questions:
                q["id"] = f"{topic_name.replace(' ', '_')}_{questions.index(q)}"
                q["difficulty"] = "medium"
            
            return questions[:8]  # Limit to 8 questions
        
        return []
        
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON parsing error for '{topic_name}': {e}")
        return []
    except Exception as e:
        print(f"❌ Error generating questions for '{topic_name}': {e}")
        return []


# ── Generate PDF ─────────────────────────────────────────────────
async def generate_pdf(
    topic_name: str,
    overview: str,
    explanations: List[Dict[str, str]],
    questions: List[Dict[str, Any]]
) -> Optional[str]:
    """
    Generate a professional PDF study guide for the topic.
    Returns path to generated PDF.
    """
    try:
        # PDF path
        safe_name = topic_name.replace(" ", "_").replace("/", "_").lower()
        pdf_path = PDF_STORAGE_DIR / f"{safe_name}.pdf"
        
        # Create PDF
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Style
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#e91e63'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            leading=14,
            alignment=4  # Justify
        )
        
        # Build content
        content = []
        
        # Title
        content.append(Paragraph(topic_name.upper(), title_style))
        content.append(Spacer(1, 0.3*inch))
        
        # Overview
        content.append(Paragraph("Overview", heading_style))
        content.append(Paragraph(overview, body_style))
        content.append(Spacer(1, 0.2*inch))
        
        # Explanations
        content.append(PageBreak())
        content.append(Paragraph("Detailed Explanations", heading_style))
        
        for exp in explanations:
            content.append(Paragraph(f"{exp['icon']} {exp['title']}", heading_style))
            content.append(Paragraph(exp["content"], body_style))
            content.append(Spacer(1, 0.15*inch))
        
        # Mock Questions
        content.append(PageBreak())
        content.append(Paragraph("Practice Questions", heading_style))
        
        questions_data = []
        for i, q in enumerate(questions[:5], 1):  # First 5 questions only
            content.append(
                Paragraph(f"<b>Q{i}.</b> {q.get('question', '')}", body_style)
            )
            
            for j, opt in enumerate(q.get("options", [])[:4], 1):
                content.append(
                    Paragraph(f"&nbsp;&nbsp;&nbsp;{chr(64+j)}. {opt}", body_style)
                )
            
            correct = q.get("correctOption", 0)
            content.append(
                Paragraph(
                    f"<b>Correct Answer:</b> {chr(65+correct)}<br/>"
                    f"<b>Explanation:</b> {q.get('explanation', '')}",
                    body_style
                )
            )
            content.append(Spacer(1, 0.2*inch))
        
        # Generate PDF
        await asyncio.to_thread(doc.build, content)
        
        return str(pdf_path)
        
    except Exception as e:
        print(f"❌ Error generating PDF for '{topic_name}': {e}")
        traceback.print_exc()
        return None


# ── MongoDB Operations ───────────────────────────────────────────
def get_mongo_client():
    """Get MongoDB client"""
    return MongoClient(MONGO_URL)


def get_all_topics(client) -> List[Dict[str, Any]]:
    """Get all topics from database"""
    try:
        db = client[DB_NAME]
        topics_collection = db["topics"]
        topics = list(topics_collection.find({}))
        return topics
    except Exception as e:
        print(f"❌ Error fetching topics: {e}")
        return []


def update_topic_with_content(
    client,
    topic_id: str,
    videos: List[Dict],
    explanations: List[Dict],
    questions: List[Dict],
    pdf_path: Optional[str]
):
    """
    Update topic document with generated content.
    """
    try:
        db = client[DB_NAME]
        topics_collection = db["topics"]
        
        update_data = {
            "recommendedVideos": videos,
            "explanations": explanations,
            "mockQuestions": questions,
            "pdfPath": pdf_path,
            "contentGeneratedAt": datetime.utcnow().isoformat(),
            "contentStatus": "complete"
        }
        
        result = topics_collection.update_one(
            {"_id": topic_id},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
        
    except Exception as e:
        print(f"❌ Error updating topic {topic_id}: {e}")
        return False


def store_mock_test(client, topic_id: str, topic_name: str, questions: List[Dict]):
    """
    Store mock test in separate collection.
    """
    try:
        db = client[DB_NAME]
        mock_tests = db["mockTests"]
        
        test_doc = {
            "topicId": topic_id,
            "topicName": topic_name,
            "questions": questions,
            "totalQuestions": len(questions),
            "duration": len(questions) * 2,  # 2 minutes per question
            "createdAt": datetime.utcnow().isoformat(),
            "difficulty": "mixed"
        }
        
        result = mock_tests.insert_one(test_doc)
        return str(result.inserted_id)
        
    except Exception as e:
        print(f"❌ Error storing mock test for {topic_name}: {e}")
        return None


# ── Main Generation Function ────────────────────────────────────
async def generate_content_for_topic(
    client,
    topic: Dict[str, Any],
    progress: Dict[str, int]
) -> bool:
    """
    Generate all content for a single topic.
    """
    try:
        topic_id = topic["_id"]
        topic_name = topic.get("topicName", "")
        language = topic.get("language", "")
        overview = topic.get("overview", "")
        difficulty = topic.get("difficulty", "Beginner")
        
        print(f"\n⏳ Processing: {topic_name} ({language})")
        
        # Step 1: Search YouTube videos
        print(f"  1. Searching YouTube videos...")
        videos = await search_youtube_videos(topic_name, language)
        print(f"     ✅ Found {len(videos)} videos")
        
        # Step 2: Generate explanations
        print(f"  2. Generating explanations (4 types)...")
        explanations = await generate_explanations(topic_name, overview, difficulty)
        print(f"     ✅ Generated {len(explanations)} explanations")
        
        # Step 3: Generate mock questions
        print(f"  3. Generating mock questions...")
        questions = await generate_mock_questions(topic_name, overview)
        print(f"     ✅ Generated {len(questions)} questions")
        
        # Step 4: Generate PDF
        print(f"  4. Generating PDF...")
        pdf_path = await generate_pdf(topic_name, overview, explanations, questions)
        if pdf_path:
            print(f"     ✅ PDF saved to {pdf_path}")
        
        # Step 5: Store in MongoDB
        print(f"  5. Storing in MongoDB...")
        update_success = update_topic_with_content(
            client, topic_id, videos, explanations, questions, pdf_path
        )
        
        # Step 6: Store mock test separately
        mock_test_id = store_mock_test(client, topic_id, topic_name, questions)
        
        if update_success and mock_test_id:
            print(f"     ✅ Successfully stored all content")
            progress["successful"] += 1
        else:
            print(f"     ⚠️  Partial success")
            progress["partial"] += 1
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing {topic_name}: {e}")
        traceback.print_exc()
        progress["failed"] += 1
        return False


# ── Main Script ─────────────────────────────────────────────────
async def main():
    """
    Main function to generate content for all 200 topics.
    """
    print("\n" + "="*80)
    print("🚀 PIXEL PIRATES - COMPLETE CONTENT GENERATION")
    print("="*80)
    
    client = get_mongo_client()
    progress = {
        "total": 0,
        "processed": 0,
        "successful": 0,
        "partial": 0,
        "failed": 0,
        "start_time": time.time()
    }
    
    try:
        # Fetch all topics
        print("\n📚 Fetching topics from database...")
        topics = get_all_topics(client)
        progress["total"] = len(topics)
        
        if not topics:
            print("❌ No topics found in database!")
            return
        
        print(f"✅ Found {progress['total']} topics")
        
        # Process topics with concurrency control
        # Process up to 2 topics concurrently to avoid rate limiting
        sem = asyncio.Semaphore(2)
        
        async def process_with_sem(topic):
            async with sem:
                await generate_content_for_topic(client, topic, progress)
                progress["processed"] += 1
                
                # Print progress every 10 topics
                if progress["processed"] % 10 == 0:
                    elapsed = time.time() - progress["start_time"]
                    print(f"\n📊 Progress: {progress['processed']}/{progress['total']} "
                          f"({100*progress['processed']//progress['total']}%) - "
                          f"Elapsed: {elapsed:.1f}s")
                
                # Add delay to avoid rate limiting
                await asyncio.sleep(2)
        
        # Process all topics
        tasks = [process_with_sem(topic) for topic in topics]
        await asyncio.gather(*tasks)
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        traceback.print_exc()
    
    finally:
        # Print final report
        elapsed = time.time() - progress["start_time"]
        
        print("\n" + "="*80)
        print("📊 GENERATION REPORT")
        print("="*80)
        print(f"Total Topics: {progress['total']}")
        print(f"Processed: {progress['processed']}")
        print(f"✅ Successful: {progress['successful']}")
        print(f"⚠️  Partial: {progress['partial']}")
        print(f"❌ Failed: {progress['failed']}")
        print(f"⏱️  Total Time: {elapsed:.1f}s")
        print(f"⚙️  Average Time per Topic: {elapsed/max(progress['processed'], 1):.1f}s")
        print("="*80 + "\n")
        
        client.close()


if __name__ == "__main__":
    asyncio.run(main())
