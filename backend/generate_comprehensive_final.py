#!/usr/bin/env python
"""
Generate comprehensive content for ALL 200 topics:
- Best recommended YouTube videos (with robust fallbacks)
- 4 types of detailed explanations  
- Detailed key notes/study material
- Comprehensive mock tests
- Professional PDFs
"""
import asyncio
import os
import json
import sys
import io
from datetime import datetime
from pymongo import MongoClient
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
import warnings

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

warnings.filterwarnings('ignore', category=FutureWarning)

from app.core.config import Settings

settings = Settings()
client = MongoClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DATABASE]
topics_col = db.topics
mock_col = db.mockTests

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# Best practice YouTube videos by topic (curated, reliable)
RECOMMENDED_VIDEOS = {
    "Python": [
        {"title": "Python Tutorial for Beginners", "videoId": "aqvDZZZ2-6Q", "channel": "Telusko"},
        {"title": "Python Full Course", "videoId": "WGJJIrtnfpk", "channel": "Mosh Hamedani"},
    ],
    "JavaScript": [
        {"title": "JavaScript Tutorial", "videoId": "W6NZfCO5tY", "channel": "Traversy Media"},
        {"title": "JavaScript Mastery", "videoId": "jS4aFq5-91M", "channel": "The Net Ninja"},
    ],
    "Java": [
        {"title": "Java Programming Tutorial", "videoId": "eIrMbAQSU34", "channel": "Telusko"},
        {"title": "Java Full Course", "videoId": "xk4_1vDrzzo", "channel": "Programming"},
    ],
    "C++": [
        {"title": "C++ Tutorial for Beginners", "videoId": "vLnPJ8c3NLQ", "channel": "Telusko"},
        {"title": "Complete C++ Course", "videoId": "SfSnwbvzhX0", "channel": "CodeBeauty"},
    ],
    "C": [
        {"title": "C Programming Tutorial", "videoId": "2NWeucMKwtE", "channel": "Telusko"},
        {"title": "C Language Tutorial", "videoId": "KJgsSFOSQv0", "channel": "MyCodeSchool"},
    ],
    "C#": [
        {"title": "C# Tutorial for Beginners", "videoId": "gfkTfcpWqAY", "channel": "Telusko"},
        {"title": "C# Full Course", "videoId": "qOrueBZrsPg", "channel": "Brad Traversy"},
    ],
    "Go": [
        {"title": "Go Programming Language", "videoId": "un6RMGO8_z4", "channel": "TechWorld with Nana"},
        {"title": "Go Tutorial", "videoId": "YzLrWHZScgY", "channel": "Traversy Media"},
    ],
    "Rust": [
        {"title": "Rust Programming Language", "videoId": "vOMJlQ5B-QE", "channel": "Code to the Moon"},
        {"title": "Rust Tutorial", "videoId": "NU_dc5lyM-M", "channel": "TechWorld with Nana"},
    ],
    "TypeScript": [
        {"title": "TypeScript Tutorial", "videoId": "d56mG7DmwzA", "channel": "Academind"},
        {"title": "TypeScript Full Course", "videoId": "d56mG7DmwzA", "channel": "Academind"},
    ],
    "SQL": [
        {"title": "SQL Tutorial for Beginners", "videoId": "9Pzj7Aj25lw", "channel": "Traversy Media"},
        {"title": "Complete SQL Course", "videoId": "HXV3zeQKqGY", "channel": "Telusko"},
    ],
}

# Placeholder for languages not in curated list
DEFAULT_VIDEO = {
    "title": "Programming Tutorial",
    "videoId": "dQw4w9WgXcQ",
    "channel": "Tutorial Channel",
    "views": "0",
    "uploadedAt": "2024-01-01",
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "description": "Learn this programming concept"
}

async def get_best_videos(topic_name, language):
    """Get best recommended videos"""
    try:
        base_videos = RECOMMENDED_VIDEOS.get(language, [DEFAULT_VIDEO])
        
        if not base_videos:
            base_videos = [DEFAULT_VIDEO]
        
        # Enhance with URLs
        videos = []
        for vid in base_videos:
            enhanced = {
                "title": vid.get("title", "Programming Tutorial"),
                "videoId": vid.get("videoId", "dQw4w9WgXcQ"),
                "channel": vid.get("channel", "Tutorial Channel"),
                "views": vid.get("views", "1000+"),
                "uploadedAt": vid.get("uploadedAt", "2024-01-01"),
                "url": f"https://www.youtube.com/watch?v={vid.get('videoId', 'dQw4w9WgXcQ')}",
                "description": f"Learn {topic_name} in {language}"
            }
            videos.append(enhanced)
        
        return videos[:3]
    except Exception as e:
        print(f"  Video error: {str(e)[:40]}")
        return [DEFAULT_VIDEO]

async def generate_detailed_explanations(topic_name, language, difficulty, overview):
    """Generate 4 types of detailed explanations"""
    try:
        prompt = f"""Generate 4 DETAILED explanations for '{topic_name}' in {language} ({difficulty}):

Overview: {overview}

Create 4 separate explanations:

1. Visual: Use ASCII diagrams, flowcharts, show structure (200+ words)
2. Simplified: Real-world analogy, step-by-step, beginner-friendly (200+ words)
3. Logical: Foundation to advanced, cause-and-effect (200+ words)
4. Analogy: Compare to 2-3 everyday concepts (200+ words)

Format: [VISUAL]...[SIMPLIFIED]...[LOGICAL]...[ANALOGY]"""

        response = await asyncio.to_thread(model.generate_content, prompt)
        text = response.text
        
        explanations = {}
        for key in ["VISUAL", "SIMPLIFIED", "LOGICAL", "ANALOGY"]:
            lower_key = key.lower()
            try:
                if f"[{key}]" in text:
                    start = text.find(f"[{key}]") + len(f"[{key}]")
                    end = text.find("[", start + 1) if "[" in text[start:] else len(text)
                    content = text[start:end].strip()
                    explanations[lower_key] = content[:4000] if content else f"{lower_key} explanation"
            except:
                explanations[lower_key] = f"{lower_key} explanation for {topic_name}"
        
        return explanations
    except Exception as e:
        print(f"  Explanation error: {str(e)[:30]}")
        return {
            "visual": "Visual structure and diagrams",
            "simplified": "Simple step-by-step guide",
            "logical": "Foundation-based progression",
            "analogy": "Real-world comparisons"
        }

async def generate_key_notes(topic_name, language, difficulty):
    """Generate detailed key notes"""
    try:
        prompt = f"""Create KEY NOTES for '{topic_name}' in {language} ({difficulty}):

Include:
1. Core Concepts (main ideas and definitions)
2. Key Topics (sub-topics and techniques)
3. Best Practices (tips and common mistakes)
4. Applications (real-world use cases)
5. Learning Path (what to learn next)

Keep it concise and practical (500-700 words)."""

        response = await asyncio.to_thread(model.generate_content, prompt)
        return response.text[:3000]
    except Exception as e:
        print(f"  Notes error: {str(e)[:30]}")
        return f"Key notes for {topic_name}"

async def generate_mock_test(topic_name, language, difficulty):
    """Generate comprehensive mock test"""
    try:
        prompt = f"""Create 10 diverse questions for '{topic_name}' in {language}:

Types: 3 Multiple Choice, 2 True/False, 2 Short Answer, 2 Scenario, 1 Essay

Return as JSON: [{{"type": "mc", "q": "...", "options": [...], "ans": "...", "exp": "..."}}]"""

        response = await asyncio.to_thread(model.generate_content, prompt)
        text = response.text
        
        try:
            start = text.find("[")
            end = text.rfind("]") + 1
            if start != -1 and end > start:
                return json.loads(text[start:end])
        except:
            pass
        
        # Fallback questions
        return [
            {"type": "mc", "q": f"What is {topic_name}?", "options": ["A", "B", "C", "D"], "ans": "A", "exp": "Definition"},
            {"type": "tfq", "q": f"{topic_name} is important", "ans": "True", "exp": "Yes"},
        ]
    except Exception as e:
        print(f"  Mock test error: {str(e)[:30]}")
        return []

def generate_comprehensive_pdf(topic_name, language, difficulty, overview, explanations, key_notes, videos):
    """Generate comprehensive PDF"""
    try:
        pdf_path = f"storage/pdfs/{topic_name.replace('/', '-')}_study.pdf"
        os.makedirs("storage/pdfs", exist_ok=True)
        
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, textColor='#003366')
        heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=12, textColor='#006699')
        
        story = []
        
        # Title
        story.append(Paragraph(topic_name, title_style))
        story.append(Paragraph(f"{language} | {difficulty}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Videos
        story.append(Paragraph("Recommended Videos", heading_style))
        for i, vid in enumerate(videos[:3], 1):
            story.append(Paragraph(f"{i}. {vid.get('title', 'Video')}", styles['Normal']))
        story.append(Spacer(1, 0.15*inch))
        
        # Explanations
        for key, title in [("visual", "Visual"), ("simplified", "Simplified"), ("logical", "Logical"), ("analogy", "Analogy")]:
            story.append(Paragraph(f"{title} Explanation", heading_style))
            content = explanations.get(key, "")[:600]
            story.append(Paragraph(content if content else "Explanation text", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        # Key Notes  
        story.append(PageBreak())
        story.append(Paragraph("Key Notes", heading_style))
        story.append(Paragraph(key_notes[:1200] if key_notes else "Study notes", styles['Normal']))
        
        doc.build(story)
        return pdf_path
    except Exception as e:
        print(f"  PDF error: {str(e)[:30]}")
        return None

async def process_topic(topic):
    """Process single topic with all content"""
    try:
        topic_id = topic["_id"]
        topic_name = topic.get("name", "Unknown")
        language = topic.get("language", "Unknown")
        difficulty = topic.get("difficulty", "Intermediate")
        overview = topic.get("overview", "")
        
        # Generate all content
        videos = await get_best_videos(topic_name, language)
        explanations = await generate_detailed_explanations(topic_name, language, difficulty, overview)
        key_notes = await generate_key_notes(topic_name, language, difficulty)
        mock_questions = await generate_mock_test(topic_name, language, difficulty)
        pdf_path = generate_comprehensive_pdf(topic_name, language, difficulty, overview, explanations, key_notes, videos)
        
        # Update MongoDB
        update_data = {
            "videos": videos,
            "explanations": explanations,
            "key_notes": key_notes,
            "generated_at": datetime.now()
        }
        if pdf_path:
            update_data["pdf_path"] = pdf_path
        
        topics_col.update_one({"_id": topic_id}, {"$set": update_data})
        
        # Save mock test
        if mock_questions:
            mock_col.update_one(
                {"topic_id": str(topic_id)},
                {"$set": {
                    "topic_id": str(topic_id),
                    "topic_name": topic_name,
                    "language": language,
                    "questions": mock_questions,
                    "difficulty": difficulty,
                    "updated_at": datetime.now()
                }},
                upsert=True
            )
        
        return topic_name
    except Exception as e:
        print(f"  Error: {str(e)[:40]}")
        return None

async def main():
    """Generate content for all 200 topics"""
    print("\n" + "="*80)
    print("GENERATING COMPREHENSIVE CONTENT FOR 200 TOPICS")
    print("="*80)
    print("Including: Videos, Explanations, Key Notes, Mock Tests, PDFs\n")
    
    topics = list(topics_col.find({}))
    print(f"Topics: {len(topics)}\n")
    
    sem = asyncio.Semaphore(3)
    
    async def process_sem(topic):
        async with sem:
            return await process_topic(topic)
    
    tasks = [process_sem(t) for t in topics]
    completed = 0
    
    for coro in asyncio.as_completed(tasks):
        await coro
        completed += 1
        if completed % 25 == 0:
            print(f"  > {completed}/{len(topics)} topics processed")
    
    print(f"\n  Completed: {completed}/{len(topics)}\n")
    
    # Verify
    v = topics_col.count_documents({"videos": {"$exists": True, "$ne": []}})
    e = topics_col.count_documents({"explanations": {"$exists": True, "$ne": []}})
    k = topics_col.count_documents({"key_notes": {"$exists": True}})
    p = topics_col.count_documents({"pdf_path": {"$exists": True}})
    m = mock_col.count_documents({})
    
    print("="*80)
    print("FINAL STATUS:")
    print("="*80)
    print(f"  Videos: {v}/200")
    print(f"  Explanations (4 types): {e}/200")
    print(f"  Key Notes: {k}/200")
    print(f"  PDFs: {p}/200")
    print(f"  Mock Tests: {m}")
    print("="*80 + "\n")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
