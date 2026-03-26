#!/usr/bin/env python
"""
Force generate questions for ALL topics - robust version with error handling
"""

import asyncio
import json
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import Settings
from app.core.database import connect_to_mongo, get_database, close_mongo_connection
from app.services.ai_content_service import AIContentGenerator
from bson import ObjectId

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class ForceQuestionGenerator:
    """Generate questions for ALL topics - with retry and error handling"""
    
    def __init__(self):
        self.settings = Settings()
        self.db = None
        self.ai_generator = AIContentGenerator()
        self.generated_count = 0
        self.failed_count = 0
        self.skipped_count = 0
    
    async def connect_db(self):
        """Connect to MongoDB"""
        try:
            success = await connect_to_mongo(self.settings)
            if success:
                self.db = await get_database()
                logger.info("✓ Connected to MongoDB")
                return self.db
            else:
                raise Exception("Failed to initialize database connection")
        except Exception as e:
            logger.error(f"✗ Failed to connect to MongoDB: {e}")
            raise

    async def generate_questions_for_topic(self, topic_id: str, topic_name: str, num_questions: int = 5) -> list:
        """Generate questions with robust error handling"""
        
        try:
            logger.info(f"📝 Generating {num_questions} questions for: {topic_name}")
            
            prompt = f"""Generate exactly {num_questions} professional multiple-choice questions about "{topic_name}".

OUTPUT FORMAT - MUST BE VALID JSON ARRAY ONLY:
[
  {{
    "id": 1,
    "question": "Clear question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correctAnswer": "Option A",
    "correctIdx": 0,
    "explanation": "Why this answer is correct.",
    "points": 10,
    "type": "mcq"
  }}
]

REQUIREMENTS:
✓ Exactly {num_questions} questions
✓ Each has exactly 4 unique options
✓ correctAnswer = text from options array
✓ correctIdx = 0-3 (position in array)
✓ Progressive difficulty (easy to hard)
✓ Test understanding, not just memorization
✓ type = "mcq"

Output ONLY the JSON array. No markdown, no code blocks. Start with [ and end with ].
"""
            
            # Call Gemini with retries
            for attempt in range(3):
                try:
                    response = await self.ai_generator.call_gemini(
                        prompt,
                        temperature=0.7,
                        max_tokens=2500,
                        retries=2
                    )
                    
                    if not response:
                        logger.warning(f"  Attempt {attempt+1}/3: Empty response")
                        if attempt < 2:
                            await asyncio.sleep(1)
                        continue
                    
                    # Clean JSON
                    response = response.strip()
                    if "```json" in response:
                        response = response.split("```json")[1].split("```")[0].strip()
                    elif "```" in response:
                        response = response.split("```")[1].split("```")[0].strip()
                    
                    # Parse
                    questions = json.loads(response)
                    
                    if not isinstance(questions, list):
                        questions = [questions] if isinstance(questions, dict) else []
                    
                    # Validate
                    validated = []
                    for idx, q in enumerate(questions, 1):
                        if not isinstance(q, dict):
                            continue
                        
                        qtext = q.get("question", "")
                        opts = q.get("options", [])
                        
                        if not qtext or len(opts) != 4:
                            continue
                        
                        correct_ans = q.get("correctAnswer", "")
                        correct_idx = q.get("correctIdx", 0)
                        
                        # Ensure correctIdx is valid
                        if isinstance(correct_idx, str):
                            try:
                                correct_idx = opts.index(correct_idx)
                            except ValueError:
                                correct_idx = 0
                        
                        validated.append({
                            "id": idx,
                            "question": qtext,
                            "options": opts,
                            "correctAnswer": str(correct_ans),
                            "correctIdx": int(correct_idx),
                            "explanation": q.get("explanation", ""),
                            "points": q.get("points", 10),
                            "type": "mcq"
                        })
                    
                    if validated:
                        logger.info(f"  ✓ Generated {len(validated)} valid questions")
                        return validated
                    else:
                        logger.warning(f"  Attempt {attempt+1}/3: No valid questions")
                        if attempt < 2:
                            await asyncio.sleep(1)
                
                except json.JSONDecodeError as e:
                    logger.warning(f"  Attempt {attempt+1}/3: JSON parse error - {str(e)[:50]}")
                    if attempt < 2:
                        await asyncio.sleep(1)
                except Exception as e:
                    logger.warning(f"  Attempt {attempt+1}/3: Error - {str(e)[:50]}")
                    if attempt < 2:
                        await asyncio.sleep(1)
            
            logger.error(f"  ✗ Failed after 3 attempts")
            return []
                
        except Exception as e:
            logger.error(f"  ✗ Error: {str(e)[:100]}")
            return []

    async def generate_for_all_topics(self):
        """Generate questions for ALL topics - no skipping"""
        
        try:
            topics_collection = self.db["topics"]
            
            # Get all topics
            all_topics = await topics_collection.find({}, {"_id": 1, "name": 1, "title": 1}).to_list(length=None)
            
            logger.info(f"📚 Processing {len(all_topics)} topics\n")
            
            for idx, topic in enumerate(all_topics, 1):
                topic_id = topic["_id"]
                topic_name = topic.get("name") or topic.get("title") or "Unknown"
                
                logger.info(f"[{idx}/{len(all_topics)}] {topic_name}")
                
                # Generate fresh questions (don't skip existing)
                questions = await self.generate_questions_for_topic(
                    str(topic_id),
                    topic_name,
                    num_questions=5
                )
                
                if questions:
                    # Store in database
                    result = await topics_collection.update_one(
                        {"_id": topic_id},
                        {"$set": {"quiz": questions}}
                    )
                    
                    if result.modified_count > 0:
                        logger.info(f"         ✅ Stored successfully\n")
                        self.generated_count += 1
                    else:
                        logger.error(f"         ❌ Failed to store in DB\n")
                        self.failed_count += 1
                else:
                    logger.error(f"         ❌ Failed to generate\n")
                    self.failed_count += 1
                
                # Rate limiting
                if idx < len(all_topics):
                    await asyncio.sleep(2)
            
            # Summary
            logger.info(f"\n{'='*60}")
            logger.info(f"✅ Generated: {self.generated_count}/{len(all_topics)}")
            logger.info(f"❌ Failed:    {self.failed_count}/{len(all_topics)}")
            logger.info(f"{'='*60}")
            
        except Exception as e:
            logger.error(f"✗ Bulk generation error: {e}")
            raise

    async def run(self):
        """Main execution"""
        try:
            await self.connect_db()
            await self.generate_for_all_topics()
        finally:
            await close_mongo_connection()


async def main():
    generator = ForceQuestionGenerator()
    await generator.run()


if __name__ == "__main__":
    asyncio.run(main())
