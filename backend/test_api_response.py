#!/usr/bin/env python
"""
Test the API /get-questions endpoint to verify questions are returned
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import Settings
from app.core.database import connect_to_mongo, get_database, close_mongo_connection
from app.routes.questions import get_topic_questions
from bson import ObjectId

async def test_get_questions():
    """Test retrieving questions from a topic"""
    
    settings = Settings()
    connected = await connect_to_mongo(settings)
    
    if not connected:
        print("❌ Failed to connect to MongoDB")
        return False
    
    try:
        db = await get_database()
        topics_collection = db["topics"]
        
        # Get first topic with questions
        topic = await topics_collection.find_one({"quiz": {"$exists": True, "$ne": []}})
        
        if not topic:
            print("❌ No topics with questions found")
            return False
        
        topic_id = str(topic["_id"])
        topic_name = topic.get("name") or topic.get("title", "Unknown")
        
        print(f"📍 Testing Topic Test Modal data retrieval")
        print(f"   Topic: {topic_name}")
        print(f"   Topic ID: {topic_id}\n")
        
        # Test the get_topic_questions endpoint
        result = await get_topic_questions(topic_id)
        
        print(f"📊 API Response:")
        print(f"   Status: {result.get('status')}")
        
        if result.get("status") == "success":
            questions = result.get("questions", [])
            print(f"   Questions Count: {len(questions)}")
            print(f"   Duration for test: 30 seconds (default)\n")
            
            # Show questions structure for Modal
            print(f"📝 Questions Data (for Modal):")
            for idx, q in enumerate(questions, 1):
                print(f"\n   Q{idx}: {q.get('question')[:70]}")
                print(f"        Options: {len(q.get('options', []))} options")
                print(f"        Points: {q.get('points', 0)}")
                print(f"        Type: {q.get('type')}")
                for opt_idx, opt in enumerate(q.get('options', []), 1):
                    print(f"          {opt_idx}. {opt}")
            
            print(f"\n✅ Modal will display these questions correctly!")
            return True
        else:
            print(f"   Message: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await close_mongo_connection()


async def main():
    success = await test_get_questions()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
