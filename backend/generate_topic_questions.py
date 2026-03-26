#!/usr/bin/env python
"""
Bulk Question Generator for All Topics
Generates MCQ questions using Gemini 2.5 Flash API for every topic in the database
and stores them in MongoDB for later retrieval.
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import Settings
from app.core.database import connect_to_mongo, get_database, close_mongo_connection
from app.services.ai_content_service import AIContentGenerator

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class TopicQuestionGenerator:
    """Generate and store questions for all topics"""
    
    def __init__(self):
        self.settings = Settings()
        self.db = None
        self.ai_generator = AIContentGenerator()
        self.generated_count = 0
        self.failed_count = 0
        self.existing_count = 0
    
    async def connect_db(self):
        """Connect to MongoDB using Motor async driver"""
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
    
    async def generate_questions_for_topic(
        self,
        topic_id: str,
        topic_name: str,
        num_questions: int = 5
    ) -> List[Dict[str, Any]]:
        """Generate questions for a single topic using Gemini"""
        
        try:
            logger.info(f"📝 Generating {num_questions} questions for: {topic_name}")
            
            prompt = f"""TASK: Generate exactly {num_questions} professional multiple-choice questions about "{topic_name}".

OUTPUT FORMAT - VALID JSON ARRAY ONLY (no markdown, no code blocks):
[
  {{
    "id": 1,
    "question": "Clear, concise question text?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correctAnswer": 0,
    "correctIdx": 0,
    "explanation": "Why this answer is correct - one clear sentence.",
    "points": 10,
    "type": "mcq"
  }}
]

CRITICAL REQUIREMENTS:
✓ Exactly {num_questions} questions in an array
✓ Each question has exactly 4 unique options
✓ correctAnswer = correct option as STRING from the options array
✓ correctIdx = 0-3 (index of correct option)
✓ explanation = clear, educational 1-2 sentence explanation
✓ type = "mcq" (Multiple Choice)
✓ points = 10 for each question
✓ id = sequential 1 to {num_questions}
✓ Questions should progressively increase in difficulty (easy → medium → hard)
✓ Questions test understanding, not just memorization
✓ Options should all be plausible but only one correct

TOPIC: {topic_name}

Examples of good questions:

For Python Topics:
- "What will this code output?" with code snippet
- "Which statement is true about [concept]?"
- "In what scenario would you use [feature]?"

For Data Structures:
- "What is the time complexity of [operation]?"
- "Which data structure is best for [use case]?"
- "What is the main advantage of [structure]?"

For Web Development:
- "What does [HTML/CSS/JS] attribute do?"
- "Which HTTP method is used for [operation]?"
- "What is the purpose of [concept]?"

Generate NOW. Output ONLY valid JSON array. Start with [ and end with ].
"""
            
            response = await self.ai_generator.call_gemini(
                prompt,
                temperature=0.7,
                max_tokens=2048,
                retries=3
            )
            
            if not response:
                logger.error(f"✗ Empty response from Gemini for {topic_name}")
                return []
            
            # Clean JSON
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            response = response.strip()
            
            # Parse JSON
            questions = json.loads(response)
            
            if not isinstance(questions, list):
                if isinstance(questions, dict) and "questions" in questions:
                    questions = questions["questions"]
                else:
                    logger.error(f"✗ Invalid JSON structure for {topic_name}")
                    return []
            
            # Validate and normalize questions
            validated_questions = []
            for idx, q in enumerate(questions, 1):
                if not isinstance(q, dict):
                    continue
                
                # Extract fields with fallbacks
                question_text = q.get("question") or q.get("question_text") or ""
                options = q.get("options") or []
                correct_answer = q.get("correctAnswer") or q.get("correct_answer")
                explanation = q.get("explanation") or ""
                points = q.get("points") or 10
                
                # If correctAnswer is an index, get the actual answer
                if isinstance(correct_answer, int) and correct_answer < len(options):
                    correct_answer = options[correct_answer]
                
                # Ensure correctIdx is an int
                correct_idx = q.get("correctIdx") or q.get("correctIdx")
                if not isinstance(correct_idx, int):
                    # Try to find it
                    if isinstance(correct_answer, str):
                        try:
                            correct_idx = options.index(correct_answer)
                        except ValueError:
                            correct_idx = 0
                    else:
                        correct_idx = 0
                
                # Validate
                if not question_text or len(options) != 4:
                    continue
                
                validated_questions.append({
                    "id": idx,
                    "question": question_text,
                    "options": options,
                    "correctAnswer": str(correct_answer),
                    "correctIdx": correct_idx,
                    "explanation": explanation,
                    "points": points,
                    "type": "mcq"
                })
            
            if validated_questions:
                logger.info(f"✓ Generated {len(validated_questions)} questions for {topic_name}")
                return validated_questions
            else:
                logger.error(f"✗ Failed to validate questions for {topic_name}")
                return []
                
        except json.JSONDecodeError as e:
            logger.error(f"✗ JSON decode error for {topic_name}: {e}")
            return []
        except Exception as e:
            logger.error(f"✗ Error generating questions for {topic_name}: {e}")
            return []
    
    async def generate_for_all_topics(self, limit: Optional[int] = None):
        """Generate questions for all topics in database"""
        
        try:
            # Get all topics using Motor async
            topics_collection = self.db["topics"]
            
            # Use Motor's async to_list() instead of find()
            all_topics = await topics_collection.find({}, {"_id": 1, "name": 1, "title": 1}).to_list(length=None)
            
            if limit:
                all_topics = all_topics[:limit]
            
            logger.info(f"📚 Found {len(all_topics)} topics to process")
            
            for idx, topic in enumerate(all_topics, 1):
                topic_id = str(topic["_id"])
                topic_name = topic.get("name") or topic.get("title") or "Unknown"
                
                # Check if topic already has questions - use Motor async
                existing_topic = await topics_collection.find_one({"_id": topic["_id"]})
                if existing_topic and existing_topic.get("quiz") and len(existing_topic["quiz"]) > 0:
                    logger.info(f"[{idx}/{len(all_topics)}] ⏭️  Skipping {topic_name} (already has {len(existing_topic['quiz'])} questions)")
                    self.existing_count += 1
                    continue
                
                # Generate questions
                questions = await self.generate_questions_for_topic(
                    topic_id,
                    topic_name,
                    num_questions=5
                )
                
                if questions:
                    # Store in database - use Motor async
                    result = await topics_collection.update_one(
                        {"_id": topic["_id"]},
                        {"$set": {"quiz": questions}}
                    )
                    
                    if result.modified_count > 0:
                        logger.info(f"[{idx}/{len(all_topics)}] ✅ Stored {len(questions)} questions for {topic_name}")
                        self.generated_count += 1
                    else:
                        logger.warning(f"[{idx}/{len(all_topics)}] ⚠️  Failed to update {topic_name} in database")
                        self.failed_count += 1
                else:
                    logger.error(f"[{idx}/{len(all_topics)}] ❌ Failed to generate questions for {topic_name}")
                    self.failed_count += 1
                
                # Rate limiting - be nice to Gemini API
                await asyncio.sleep(2)
            
            # Print summary
            self._print_summary(len(all_topics))
            
        except Exception as e:
            logger.error(f"✗ Error in bulk generation: {e}")
            raise
    
    def _print_summary(self, total: int):
        """Print generation summary"""
        print("\n" + "="*60)
        print("📊 QUESTION GENERATION SUMMARY")
        print("="*60)
        print(f"Total Topics:        {total}")
        print(f"✅ Successfully Generated:  {self.generated_count}")
        print(f"⏭️  Already Existed:       {self.existing_count}")
        print(f"❌ Failed:            {self.failed_count}")
        print(f"Pending:             {total - self.generated_count - self.existing_count}")
        print("="*60 + "\n")
    
    async def run(self, limit: Optional[int] = None):
        """Main execution"""
        try:
            await self.connect_db()
            await self.generate_for_all_topics(limit)
        finally:
            await close_mongo_connection()

async def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate questions for all topics")
    parser.add_argument("--limit", type=int, help="Limit number of topics to process")
    parser.add_argument("--topic", type=str, help="Generate for specific topic name")
    args = parser.parse_args()
    
    generator = TopicQuestionGenerator()
    
    try:
        if args.topic:
            logger.info(f"📝 Generating questions for topic: {args.topic}")
            await generator.connect_db()
            questions = await generator.generate_questions_for_topic(
                topic_id="custom",
                topic_name=args.topic,
                num_questions=5
            )
            print(json.dumps(questions, indent=2))
        else:
            await generator.run(limit=args.limit)
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())
