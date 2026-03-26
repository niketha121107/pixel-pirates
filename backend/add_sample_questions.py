#!/usr/bin/env python
"""
Quick test to populate a topic with sample questions
for testing the Topic Test Modal frontend
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import Settings
from app.core.database import connect_to_mongo, get_database, close_mongo_connection
from bson import ObjectId
import json

async def add_sample_questions():
    """Add sample MCQ questions to the first topic"""
    
    settings = Settings()
    connected = await connect_to_mongo(settings)
    
    if not connected:
        print("❌ Failed to connect to MongoDB")
        return False
    
    try:
        db = await get_database()
        topics_collection = db["topics"]
        
        # Get first topic
        first_topic = await topics_collection.find_one({})
        
        if not first_topic:
            print("❌ No topics found")
            return False
        
        topic_name = first_topic.get("name") or first_topic.get("title", "Unknown")
        topic_id = first_topic["_id"]
        
        print(f"📍 Adding sample questions to: {topic_name}")
        
        # Sample questions
        sample_questions = [
            {
                "id": 1,
                "question": "What is a variable in programming?",
                "options": [
                    "A container for storing data values",
                    "A function that returns values",
                    "A type of loop",
                    "A class definition"
                ],
                "correctAnswer": "A container for storing data values",
                "correctIdx": 0,
                "explanation": "A variable is named storage location that holds a value and can be referenced by name.",
                "points": 10,
                "type": "mcq"
            },
            {
                "id": 2,
                "question": "Which of the following is NOT a valid variable name?",
                "options": [
                    "my_variable",
                    "2_variables",
                    "myVariable",
                    "_hidden"
                ],
                "correctAnswer": "2_variables",
                "correctIdx": 1,
                "explanation": "Variable names cannot start with a number. They must begin with a letter or underscore.",
                "points": 10,
                "type": "mcq"
            },
            {
                "id": 3,
                "question": "What is the scope of a variable?",
                "options": [
                    "The time it takes to execute",
                    "The region of code where variable can be accessed",
                    "The memory size it occupies",
                    "How many times it can be used"
                ],
                "correctAnswer": "The region of code where variable can be accessed",
                "correctIdx": 1,
                "explanation": "Scope defines the visibility and lifetime of a variable in a program.",
                "points": 10,
                "type": "mcq"
            },
            {
                "id": 4,
                "question": "What is the difference between local and global variables?",
                "options": [
                    "Global variables are faster",
                    "Local variables are only accessible within their function/block; globals are accessible anywhere",
                    "There is no difference",
                    "Global variables store different data types"
                ],
                "correctAnswer": "Local variables are only accessible within their function/block; globals are accessible anywhere",
                "correctIdx": 1,
                "explanation": "Local variables are scoped to functions/blocks while global variables have file or program scope.",
                "points": 10,
                "type": "mcq"
            },
            {
                "id": 5,
                "question": "How would you declare a variable to be constant?",
                "options": [
                    "use let const myVar = 5",
                    "const myVar = 5 (JavaScript) or final type myVar = 5 (Java)",
                    "constant myVar = 5",
                    "make_it_const(myVar)"
                ],
                "correctAnswer": "const myVar = 5 (JavaScript) or final type myVar = 5 (Java)",
                "correctIdx": 1,
                "explanation": "Different languages use different keywords for constants: const in JavaScript, final in Java, const in C++.",
                "points": 10,
                "type": "mcq"
            }
        ]
        
        # Update topic with questions
        result = await topics_collection.update_one(
            {"_id": topic_id},
            {"$set": {"quiz": sample_questions}}
        )
        
        if result.modified_count > 0:
            print(f"✅ Added {len(sample_questions)} sample questions to {topic_name}")
            print(f"\n📋 Questions added (Topic ID: {topic_id}):")
            for q in sample_questions:
                print(f"  {q['id']}. {q['question'][:60]}...")
            return True
        else:
            print("❌ Failed to update topic")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await close_mongo_connection()


async def main():
    success = await add_sample_questions()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
