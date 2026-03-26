#!/usr/bin/env python3
"""
Force generate questions for all topics with AGGRESSIVE rate limiting
Respects Gemini free tier quota (very low limits)
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from bson import ObjectId

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_content_service import AIContentGenerator
from app.core.config import settings


class RateLimitedQuestionGenerator:
    def __init__(self):
        self.ai_generator = AIContentGenerator()
        self.db: AsyncIOMotorDatabase | None = None
        self.generated_count = 0
        self.failed_count = 0
        self.request_count = 0
        self.quota_hit = False

    async def get_database(self) -> AsyncIOMotorDatabase:
        """Get database connection"""
        if self.db is None:
            client = AsyncIOMotorClient(settings.MONGODB_URL)
            self.db = client[settings.MONGODB_DATABASE]
        return self.db

    async def wait_for_quota(self, seconds: int = 15):
        """Wait with countdown display"""
        for i in range(seconds, 0, -1):
            print(f"⏳ Rate limit: waiting {i}s...", end="\r")
            await asyncio.sleep(1)
        print("                              ")  # Clear line

    async def generate_questions_for_topic(self, topic_id: str, topic_name: str, num_questions: int = 5) -> list:
        """Generate questions with robust retry and quota handling"""
        
        prompt = f"""Generate exactly {num_questions} multiple-choice questions for "{topic_name}".

Return ONLY valid JSON in this exact format:
[
  {{
    "question": "Question text?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correctAnswer": "The correct option text",
    "explanation": "Why this is correct and others are wrong"
  }}
]

Important: 
- Each question MUST have exactly 4 options
- correctAnswer must be the exact text from options array
- Make questions progressively harder
- No extra text, only JSON"""

        last_error = None
        
        for attempt in range(3):
            try:
                # Add delay before each request (aggressive rate limiting)
                if attempt > 0:
                    await self.wait_for_quota(seconds=10)
                
                self.request_count += 1
                print(f"   [Attempt {attempt + 1}/3] Calling API (request #{self.request_count})...")
                
                response = await self.ai_generator.call_gemini(prompt, max_tokens=2000)
                
                if not response or response.strip() == "":
                    print(f"   ⚠️  Attempt {attempt + 1}/3: Empty response")
                    if attempt < 2:
                        await self.wait_for_quota(seconds=10)
                    continue

                # Try to parse JSON
                try:
                    questions_data = json.loads(response.strip())
                except json.JSONDecodeError as e:
                    print(f"   ⚠️  Attempt {attempt + 1}/3: Invalid JSON ({str(e)[:30]})")
                    if attempt < 2:
                        await self.wait_for_quota(seconds=10)
                    continue

                # Validate structure
                if not isinstance(questions_data, list) or len(questions_data) == 0:
                    print(f"   ⚠️  Attempt {attempt + 1}/3: Invalid structure (not a list or empty)")
                    if attempt < 2:
                        await self.wait_for_quota(seconds=10)
                    continue

                # Validate each question
                validated_questions = []
                for q in questions_data:
                    if all(k in q for k in ["question", "options", "correctAnswer", "explanation"]):
                        if len(q["options"]) == 4:
                            validated_questions.append({
                                "question": q["question"],
                                "options": q["options"],
                                "correctAnswer": q["correctAnswer"],
                                "explanation": q["explanation"],
                                "type": "mcq",
                                "points": 10
                            })

                if len(validated_questions) == num_questions:
                    print(f"   ✓ Generated {len(validated_questions)} valid questions")
                    return validated_questions
                else:
                    print(f"   ⚠️  Attempt {attempt + 1}/3: Only {len(validated_questions)}/{num_questions} valid")
                    if attempt < 2:
                        await self.wait_for_quota(seconds=10)

            except Exception as e:
                last_error = str(e)
                if "429" in last_error or "quota" in last_error.lower():
                    print(f"   ⚠️  QUOTA HIT: {last_error[:50]}")
                    self.quota_hit = True
                    if attempt < 2:
                        await self.wait_for_quota(seconds=30)  # Long wait on quota
                else:
                    print(f"   ⚠️  Attempt {attempt + 1}/3: {last_error[:50]}")
                    if attempt < 2:
                        await self.wait_for_quota(seconds=10)

        print(f"   ✗ Failed after 3 attempts")
        return []

    async def generate_for_all_topics(self):
        """Generate questions for all topics with rate limiting"""
        db = await self.get_database()
        topics_collection = db["topics"]

        print("\n" + "=" * 60)
        print("🚀 Starting question generation (RATE LIMITED)")
        print("⚠️  API Quota: Very limited on free tier")
        print("⏳ Expect: ~5-10 minutes for all 200 topics")
        print("=" * 60 + "\n")

        # Get all topics
        all_topics = await topics_collection.find({}, {"_id": 1, "name": 1, "title": 1}).to_list(length=None)
        total_topics = len(all_topics)
        
        print(f"📋 Found {total_topics} topics to process\n")

        for idx, topic in enumerate(all_topics, 1):
            topic_id = topic.get("_id")
            topic_name = topic.get("title") or topic.get("name", "Unknown")

            print(f"[{idx}/{total_topics}] {topic_name}")

            # Generate questions
            questions = await self.generate_questions_for_topic(str(topic_id), topic_name)

            if questions:
                # Store in database
                try:
                    await topics_collection.update_one(
                        {"_id": topic_id},
                        {"$set": {"quiz": questions}}
                    )
                    self.generated_count += 1
                    print(f"   ✅ Stored successfully to database\n")
                except Exception as e:
                    self.failed_count += 1
                    print(f"   ❌ Failed to store: {str(e)[:50]}\n")
            else:
                self.failed_count += 1
                print(f"   ❌ Failed to generate\n")

            # AGGRESSIVE rate limiting between topics
            if idx < total_topics:
                if self.quota_hit:
                    print(f"⏳ Quota alert: Waiting 45s before next topic...")
                    await self.wait_for_quota(seconds=45)
                    self.quota_hit = False
                else:
                    await self.wait_for_quota(seconds=15)

        # Print summary
        print("\n" + "=" * 60)
        print(f"✅ Generated: {self.generated_count}/{total_topics}")
        print(f"❌ Failed: {self.failed_count}/{total_topics}")
        print(f"📊 Total API requests made: {self.request_count}")
        print("=" * 60)

    async def main(self):
        """Main entry point"""
        try:
            await self.generate_for_all_topics()
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
        except Exception as e:
            print(f"\n\n❌ Fatal error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.db:
                self.db.client.close()


if __name__ == "__main__":
    try:
        asyncio.run(RateLimitedQuestionGenerator().main())
    except KeyboardInterrupt:
        print("\n\nGenerator stopped.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
