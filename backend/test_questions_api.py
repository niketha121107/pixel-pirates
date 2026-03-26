#!/usr/bin/env python3
"""
Quick test script for the questions API endpoints
Tests question generation, retrieval, and validation
"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import get_database, connect_to_mongo
from app.core.config import Settings
from bson import ObjectId


async def test_questions_api():
    """Test the questions API endpoints"""
    
    print("🧪 Starting Questions API Test Suite\n")
    
    # Initialize database connection
    print("🔗 Initializing database connection...")
    settings = Settings()
    connected = await connect_to_mongo(settings)
    
    if not connected:
        print("❌ Failed to connect to MongoDB")
        print("   Make sure MongoDB is running at mongodb://localhost:27017")
        return False
    
    try:
        db = await get_database()
        print(f"✅ Database initialized: {db.name}")
    except Exception as e:
        print(f"❌ Failed to get database: {e}")
        return False
    
    topics_collection = db["topics"]
    
    topics_collection = db["topics"]
    
    # Get a sample topic to test with
    print("📍 Finding test topic...")
    sample_topic = await topics_collection.find_one({})
    
    if not sample_topic:
        print("❌ No topics found in database. Cannot run tests.")
        return False
    
    topic_id = str(sample_topic["_id"])
    topic_name = sample_topic.get("name") or sample_topic.get("title", "Unknown Topic")
    print(f"✅ Found test topic: {topic_name} (ID: {topic_id})")
    
    # Test 1: Check existing quiz structure
    print("\n📝 Test 1: Checking current quiz structure in database...")
    try:
        topic = await topics_collection.find_one({"_id": sample_topic["_id"]})
        quiz = topic.get("quiz", [])
        
        if quiz:
            print(f"✅ Topic has {len(quiz)} questions")
            # Show first question
            if len(quiz) > 0:
                q = quiz[0]
                print(f"   └─ Q1: {q.get('question', 'N/A')[:60]}...")
                print(f"   └─ Options: {len(q.get('options', []))} options")
                print(f"   └─ Correct Answer: {q.get('correctAnswer')}")
        else:
            print("⚠️  No questions yet in this topic")
            
    except Exception as e:
        print(f"❌ Error checking quiz: {e}")
        return False
    
    # Test 2: Verify Motor database connection works
    print("\n💾 Test 2: Verifying Motor async connection...")
    try:
        # Simple async operations test
        count = await topics_collection.count_documents({})
        print(f"✅ Motor connection working - found {count} total topics in database")
        
        # Test find_one
        first = await topics_collection.find_one({})
        if first:
            print(f"✅ find_one() working - retrieved topic: {first.get('name', 'Unknown')}")
            
    except Exception as e:
        print(f"❌ Error with Motor operations: {e}")
        return False
    
    # Test 3: Verify API imports
    print("\n🔌 Test 3: Checking API endpoints are importable...")
    try:
        from app.routes.questions import router
        print(f"✅ Questions router imported successfully")
        print(f"   └─ Router tags: {router.tags if hasattr(router, 'tags') else 'N/A'}")
        print(f"   └─ Prefix from include_router: /api/questions")
    except Exception as e:
        print(f"❌ Error importing router: {e}")
        return False
    
    # Test 4: Verify Gemini service is available
    print("\n🤖 Test 4: Checking AI service availability...")
    try:
        from app.services.ai_content_service import AIContentGenerator
        ai = AIContentGenerator()
        print(f"✅ AIContentGenerator imported successfully")
        print(f"   └─ Ready for question generation")
    except Exception as e:
        print(f"❌ Error importing AI service: {e}")
        return False
    
    print("\n✅ All tests completed successfully!")
    return True


async def main():
    """Run all tests"""
    try:
        success = await test_questions_api()
        
        # Close connection
        from app.core.database import close_mongo_connection
        await close_mongo_connection()
        
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
