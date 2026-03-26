#!/usr/bin/env python3
"""
Seed questions for all 200 topics using deterministic generation
Questions are generated programmatically based on topic names
"""

import asyncio
import json
import sys
import os
import random
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from bson import ObjectId

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings


class QuestionSeeder:
    """Generate seeded questions for topics"""
    
    # Question templates organized by common programming topics
    TEMPLATES = {
        "syntax": {
            "questions": [
                "What is the correct syntax for {}?",
                "Which of the following is valid {} syntax?",
                "What will happen with this {} code?",
                "Identify the syntax error in this {}:",
                "What does this {} expression evaluate to?",
            ],
            "options_base": [
                "Correct implementation",
                "Missing semicolon",
                "Invalid variable name",
                "Undefined function call",
            ]
        },
        "concept": {
            "questions": [
                "What is the main purpose of {}?",
                "Which statement best describes {}?",
                "How does {} work in programming?",
                "What is the key principle behind {}?",
                "When should you use {}?",
            ],
            "options_base": [
                "Improve code organization",
                "Reduce memory usage",
                "Speed up execution",
                "Simplify debugging",
            ]
        },
        "error": {
            "questions": [
                "What error occurs with this {} code?",
                "How would you fix this {} issue?",
                "Why does this {} code fail?",
                "What is the problem with this {} implementation?",
                "Which {} error is most common?",
            ],
            "options_base": [
                "TypeError",
                "RuntimeError",
                "NameError",
                "ValueError",
            ]
        },
        "best_practice": {
            "questions": [
                "What is the best practice for {}?",
                "Which approach to {} is most efficient?",
                "How should {} be properly implemented?",
                "What is the recommended way to use {}?",
                "Which coding standard applies to {}?",
            ],
            "options_base": [
                "Use descriptive names",
                "Keep functions small",
                "Add comprehensive comments",
                "Avoid global variables",
            ]
        },
    }

    # Topic category detection keywords
    CATEGORY_KEYWORDS = {
        "syntax": ["syntax", "variable", "statement", "operator", "declaration"],
        "concept": ["concept", "principle", "theory", "fundamentals", "basics", "architecture", "design", "pattern"],
        "error": ["error", "exception", "debug", "debugging", "bug", "issue"],
        "best_practice": ["best practice", "convention", "standard", "optimization", "performance", "refactor"],
    }

    def __init__(self):
        self.db: AsyncIOMotorDatabase | None = None
        self.generated_count = 0
        self.failed_count = 0

    async def get_database(self) -> AsyncIOMotorDatabase:
        """Get database connection"""
        if self.db is None:
            client = AsyncIOMotorClient(settings.MONGODB_URL)
            self.db = client[settings.MONGODB_DATABASE]
        return self.db

    def categorize_topic(self, topic_name: str) -> str:
        """Categorize topic based on keywords"""
        topic_lower = topic_name.lower()
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(keyword in topic_lower for keyword in keywords):
                return category
        
        # Default to concept if no match
        return "concept"

    def generate_options(self, template_options: list, topic_name: str, seed_idx: int) -> tuple:
        """Generate 4 unique options for a question (returns options list and correct index)"""
        random.seed(hash(f"{topic_name}_{seed_idx}_options"))
        
        # Vary which option is the correct answer based on seed_idx
        correct_idx_in_template = seed_idx % len(template_options)
        correct_answer = template_options[correct_idx_in_template]
        
        # Build options array with varied selection
        options = []
        for i in range(4):
            # Ensure we get different options, starting from different positions
            option_idx = (i + seed_idx) % len(template_options)
            options.append(template_options[option_idx])
        
        # Shuffle to randomize correct answer position
        random.shuffle(options)
        correct_idx = options.index(correct_answer)
        
        return options, correct_idx

    def generate_questions_for_topic(self, topic_name: str, topic_id: str) -> list:
        """Generate 5 seeded questions for a topic"""
        # Categorize the topic
        category = self.categorize_topic(topic_name)
        template = self.TEMPLATES[category]
        
        questions = []
        random.seed(hash(f"{topic_name}_{topic_id}"))
        
        for i in range(5):
            # Select question template
            question_template = template["questions"][i % len(template["questions"])]
            question_text = question_template.format(f'"{topic_name}"')
            
            # Generate options and get correct index
            base_options = template["options_base"].copy()
            options, correct_idx = self.generate_options(base_options, topic_name, i)
            
            # Correct answer is the one at the correct index
            correct_answer = options[correct_idx]
            
            # Create explanation
            explanations = [
                f"This relates to the fundamental principle of {topic_name}.",
                f"Understanding {topic_name} is essential for clean code.",
                f"{topic_name} helps maintain code quality and readability.",
                f"The best practice for {topic_name} ensures maintainability.",
                f"Proper use of {topic_name} prevents common bugs.",
            ]
            explanation = explanations[i % len(explanations)]
            
            questions.append({
                "id": i + 1,
                "question": question_text,
                "options": options,
                "correctAnswer": correct_answer,
                "correctIdx": correct_idx,
                "explanation": explanation,
                "points": 10,
                "type": "mcq"
            })
        
        return questions

    async def seed_all_topics(self):
        """Seed questions for all topics"""
        db = await self.get_database()
        topics_collection = db["topics"]

        print("\n" + "=" * 70)
        print("🌱 SEEDING QUESTIONS FOR ALL TOPICS")
        print("=" * 70 + "\n")

        # Get all topics
        all_topics = await topics_collection.find({}, {"_id": 1, "name": 1, "title": 1}).to_list(length=None)
        total_topics = len(all_topics)
        
        print(f"📋 Found {total_topics} topics to seed\n")

        for idx, topic in enumerate(all_topics, 1):
            topic_id = topic.get("_id")
            topic_name = topic.get("title") or topic.get("name", "Unknown")

            print(f"[{idx:3d}/{total_topics}] {topic_name[:45]:<45}", end=" ")

            try:
                # Check if questions already exist
                existing = await topics_collection.find_one({"_id": topic_id})
                if existing and existing.get("quiz") and len(existing["quiz"]) > 0:
                    print(f"✓ Already has {len(existing['quiz'])} questions")
                    self.generated_count += 1
                    continue

                # Generate seeded questions
                questions = self.generate_questions_for_topic(topic_name, str(topic_id))

                # Store in database
                await topics_collection.update_one(
                    {"_id": topic_id},
                    {"$set": {"quiz": questions}}
                )
                
                self.generated_count += 1
                print(f"✅ Seeded 5 questions")

            except Exception as e:
                self.failed_count += 1
                print(f"❌ Failed: {str(e)[:40]}")

        # Print summary
        print("\n" + "=" * 70)
        print(f"✅ SEEDING COMPLETE")
        print(f"📊 Seeded/Verified: {self.generated_count}/{total_topics}")
        print(f"❌ Failed: {self.failed_count}/{total_topics}")
        print(f"⏱️  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70 + "\n")

        if self.failed_count == 0:
            print("🎉 All topics now have questions! The UI is ready to use.")
            print("📝 Questions are deterministically generated based on topic names.")
            print("🔄 To regenerate with new questions, delete the 'quiz' field from topics.\n")

    async def main(self):
        """Main entry point"""
        try:
            await self.seed_all_topics()
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
        except Exception as e:
            print(f"\n\n❌ Fatal error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.db is not None:
                self.db.client.close()


if __name__ == "__main__":
    try:
        asyncio.run(QuestionSeeder().main())
    except KeyboardInterrupt:
        print("\n\nSeeder stopped.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
