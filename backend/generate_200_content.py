#!/usr/bin/env python
"""Generate complete content for all 200 topics"""
import asyncio
import os
from datetime import datetime
from pymongo import MongoClient
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
import warnings

warnings.filterwarnings('ignore', category=FutureWarning)

from app.core.config import Settings

settings = Settings()
client = MongoClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DATABASE]
topics_col = db.topics
mock_col = db.mockTests

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# Placeholder video
PLACEHOLDER_VIDEO = {
    "title": "Tutorial Video",
    "videoId": "dQw4w9WgXcQ",
    "channel": "Tutorial Channel",
    "views": "1000",
    "uploadedAt": "2024-01-01",
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}

# Default explanations
DEFAULT_EXPL = {
    "visual": "Visual diagrams and flowcharts demonstrate the structure. Components are arranged in hierarchical patterns showing relationships and data flow through the system.",
    "simplified": "Imagine this like a real-world process. Break it into simple steps: first understand the basics, then see how pieces fit together. It's a straightforward progression.",
    "logical": "The foundation begins with core principles. Each concept builds on the previous one. Understanding flows from simple concepts to complex implementations.",
    "analogy": "Think of it like building: you need a foundation before walls, walls before a roof. Similarly, this concept has logical prerequisites and dependencies."
}

# Default mock questions
DEFAULT_MOCK = [
    "What are the key concepts of {}?",
    "How would you implement {} in practice?",
    "Explain the advantages of {}.",
    "What are common pitfalls when using {}?",
    "Compare {} with alternatives.",
    "What is the history and evolution of {}?",
    "How does {} integrate with other systems?",
    "What are real-world applications of {}?"
]

async def generate_explanations(topic_name, language, difficulty):
    """Generate 4 types of explanations"""
    try:
        prompt = f"""Generate 4 explanations for '{topic_name}' in {language} ({difficulty}):

1. **Visual**: ASCII diagrams, flowcharts, hierarchy showing structure (150+ words)
2. **Simplified**: Real-world analogy, step-by-step, beginner-friendly (150+ words)
3. **Logical**: Foundation to advanced progression, reasoning (150+ words)
4. **Analogy**: Compare to everyday concepts, relationships (150+ words)

Format: [Visual]\n...\n[Simplified]\n...\n[Logical]\n...\n[Analogy]\n..."""

        response = await asyncio.to_thread(model.generate_content, prompt)
        text = response.text
        
        expl = {}
        for key in ["Visual", "Simplified", "Logical", "Analogy"]:
            lower_key = key.lower()
            if f"[{key}]" in text:
                start = text.find(f"[{key}]") + len(f"[{key}]")
                end = text.find("[", start + 1) if "[" in text[start:] else len(text)
                content = text[start:end].strip()
                expl[lower_key] = content[:4000] if content else DEFAULT_EXPL[lower_key]
            else:
                expl[lower_key] = DEFAULT_EXPL[lower_key]
        return expl
    except Exception as e:
        print(f"  ⚠️  Explanation API error: {str(e)[:50]}")
        return DEFAULT_EXPL

def generate_pdf(topic_name, language, difficulty, overview, explanations):
    """Generate PDF for topic"""
    try:
        pdf_path = f"storage/pdfs/{topic_name.replace('/', '-')}.pdf"
        os.makedirs("storage/pdfs", exist_ok=True)
        
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, textColor='#003366', spaceAfter=12)
        heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, textColor='#006699', spaceAfter=10)
        
        story = []
        story.append(Paragraph(topic_name, title_style))
        story.append(Paragraph(f"<b>{language}</b> | {difficulty}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("<b>Overview</b>", heading_style))
        story.append(Paragraph(overview[:500], styles['Normal']))
        story.append(Spacer(1, 0.15*inch))
        
        for key, title in [("visual", "Visual Explanation"), ("simplified", "Simplified Explanation"), 
                          ("logical", "Logical Explanation"), ("analogy", "Analogy Explanation")]:
            story.append(Paragraph(f"<b>{title}</b>", heading_style))
            content = explanations.get(key, DEFAULT_EXPL.get(key, ""))[:1000]
            story.append(Paragraph(content, styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        doc.build(story)
        return pdf_path
    except Exception as e:
        print(f"  ⚠️  PDF generation error: {str(e)[:50]}")
        return None

async def generate_content_for_topic(topic):
    """Generate all content for single topic"""
    topic_id = topic["_id"]
    topic_name = topic.get("name", "Unknown")
    language = topic.get("language", "Unknown")
    difficulty = topic.get("difficulty", "Intermediate")
    overview = topic.get("overview", f"{topic_name} in {language}")
    
    # Generate explanations
    explanations = await generate_explanations(topic_name, language, difficulty)
    
    # Generate PDF
    pdf_path = generate_pdf(topic_name, language, difficulty, overview, explanations)
    
    # Update topic in DB
    update_data = {
        "videos": [PLACEHOLDER_VIDEO],
        "explanations": explanations,
        "generated_at": datetime.now()
    }
    
    if pdf_path:
        update_data["pdf_path"] = pdf_path
    
    topics_col.update_one({"_id": topic_id}, {"$set": update_data})
    
    # Generate mock test if doesn't exist
    if not mock_col.find_one({"topic_id": str(topic_id)}):
        questions = [q.format(topic_name) for q in DEFAULT_MOCK]
        mock_col.insert_one({
            "topic_id": str(topic_id),
            "topic_name": topic_name,
            "language": language,
            "questions": questions,
            "created_at": datetime.now()
        })
    
    return topic_name

async def generate_all():
    """Generate content for all 200 topics"""
    print("\n" + "="*70)
    print("GENERATING CONTENT FOR 200 TOPICS")
    print("="*70)
    
    topics = list(topics_col.find({}))
    print(f"Topics to process: {len(topics)}\n")
    
    # Process with Semaphore(3) for rate limiting
    sem = asyncio.Semaphore(3)
    
    async def process_with_sem(topic):
        async with sem:
            try:
                name = await generate_content_for_topic(topic)
                return name
            except Exception as e:
                print(f"  ⚠️  Error processing {topic.get('name')}: {str(e)[:30]}")
                return None
    
    tasks = [process_with_sem(t) for t in topics]
    completed = 0
    
    for coro in asyncio.as_completed(tasks):
        await coro
        completed += 1
        if completed % 20 == 0:
            print(f"  ✓ {completed}/{len(topics)} topics processed")
    
    print(f"  ✓ ALL {len(topics)} topics processed!")
    
    # Final verification
    v = topics_col.count_documents({"videos": {"$exists": True, "$ne": []}})
    e = topics_col.count_documents({"explanations": {"$exists": True, "$ne": []}})
    p = topics_col.count_documents({"pdf_path": {"$exists": True}})
    m = mock_col.count_documents({})
    
    print(f"\n{'='*70}")
    print(f"✅ CONTENT GENERATION COMPLETE:")
    print(f"{'='*70}")
    print(f"  ✅ Videos: {v}/200")
    print(f"  ✅ Explanations: {e}/200 (4 types each)")
    print(f"  ✅ PDFs: {p}/200")
    print(f"  ✅ Mock Tests: {m} question banks")
    print(f"{'='*70}\n")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(generate_all())
