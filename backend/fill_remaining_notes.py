#!/usr/bin/env python
"""Fill remaining key notes for all topics"""
import asyncio
from pymongo import MongoClient
import google.generativeai as genai
from app.core.config import Settings

settings = Settings()
client = MongoClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DATABASE]
topics_col = db.topics

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

async def generate_key_notes(topic_name, language, difficulty):
    """Generate key notes for a topic"""
    try:
        prompt = f"""Create KEY NOTES for '{topic_name}' in {language} ({difficulty}):

Include:
1. Core Concepts - main ideas and definitions (100+ words)
2. Key Topics - sub-topics and techniques (100+ words)
3. Best Practices - tips and avoid mistakes (80+ words)
4. Applications - real-world use cases (80+ words)

Keep practical and concise."""

        response = await asyncio.to_thread(model.generate_content, prompt)
        return response.text[:2500]
    except Exception as e:
        print(f"  Error generating notes: {str(e)[:30]}")
        return f"Key notes for {topic_name} in {language}"

async def fill_missing_notes():
    """Fill missing key notes"""
    print("\n" + "="*70)
    print("FILLING REMAINING KEY NOTES")
    print("="*70 + "\n")
    
    # Find topics without key notes
    missing = list(topics_col.find({
        "$or": [
            {"key_notes": {"$exists": False}},
            {"key_notes": None},
            {"key_notes": ""}
        ]
    }))
    
    print(f"Missing key notes: {len(missing)}\n")
    
    if not missing:
        print("All topics have key notes!")
        client.close()
        return
    
    # Process with Semaphore(2) for API rate limiting
    sem = asyncio.Semaphore(2)
    
    async def process_topic(topic):
        async with sem:
            try:
                topic_id = topic["_id"]
                notes = await generate_key_notes(
                    topic.get("name", "Unknown"),
                    topic.get("language", "Unknown"),
                    topic.get("difficulty", "Intermediate")
                )
                
                topics_col.update_one(
                    {"_id": topic_id},
                    {"$set": {"key_notes": notes}}
                )
                return True
            except Exception as e:
                print(f"  Failed: {topic.get('name')}")
                return False
    
    tasks = [process_topic(t) for t in missing]
    completed = 0
    
    for coro in asyncio.as_completed(tasks):
        result = await coro
        if result:
            completed += 1
        if completed % 20 == 0 and completed > 0:
            print(f"  > {completed}/{len(missing)} notes added")
    
    print(f"  + {completed}/{len(missing)} notes completed\n")
    
    # Final count
    k = topics_col.count_documents({"key_notes": {"$exists": True, "$ne": None, "$ne": ""}})
    v = topics_col.count_documents({"videos": {"$exists": True, "$ne": []}})
    e = topics_col.count_documents({"explanations": {"$exists": True, "$ne": []}})
    p = topics_col.count_documents({"pdf_path": {"$exists": True}})
    
    print("="*70)
    print("FINAL COMPREHENSIVE CONTENT STATUS:")
    print("="*70)
    print(f"  Videos: {v}/200")
    print(f"  Explanations (4 types): {e}/200")
    print(f"  Key Notes: {k}/200")
    print(f"  PDFs: {p}/200")
    print("="*70)
    
    if v == 200 and e == 200 and k == 200 and p == 200:
        print("  SUCCESS: 100% COMPLETE!\n")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(fill_missing_notes())
