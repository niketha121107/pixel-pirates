"""
Simple MongoDB Database Initialization Script
Sets up basic collections and indexes without external dependencies
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def simple_init_database():
    """Initialize MongoDB database with basic setup"""
    logger.info("🚀 Starting MongoDB database initialization...")
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(
            "mongodb://localhost:27017/",
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )
        
        # Verify connection
        await client.admin.command('ping')
        logger.info("✅ MongoDB connection successful!")
        
        # Get database
        db = client["pixel_pirates"]
        logger.info("✅ Connected to database: pixel_pirates")
        
        # Create collections and indexes
        logger.info("📋 Creating collections and indexes...")
        
        # Users collection with indexes
        await db["users"].create_index("email", unique=True)
        await db["users"].create_index("id", unique=True)
        logger.info("✅ Created users collection with indexes")
        
        # Topics collection with indexes
        await db["topics"].create_index("id", unique=True)
        await db["topics"].create_index([("language", 1), ("difficulty", 1)])
        logger.info("✅ Created topics collection with indexes")
        
        # User Progress collection with indexes
        await db["user_progress"].create_index([("user_id", 1), ("topic_id", 1)], unique=True)
        await db["user_progress"].create_index("user_id")
        logger.info("✅ Created user_progress collection with indexes")
        
        # Videos collection with indexes
        await db["videos"].create_index("id", unique=True)
        await db["videos"].create_index("youtube_id", unique=True)
        await db["videos"].create_index([("language", 1), ("topic", 1)])
        logger.info("✅ Created videos collection with indexes")
        
        # Quizzes collection with indexes  
        await db["quizzes"].create_index("id", unique=True)
        await db["quizzes"].create_index("topic_id")
        logger.info("✅ Created quizzes collection with indexes")
        
        # Analytics collection with indexes
        await db["analytics"].create_index([("user_id", 1), ("date", 1)])
        await db["analytics"].create_index("user_id")
        logger.info("✅ Created analytics collection with indexes")
        
        # Leaderboard collection with indexes
        await db["leaderboard"].create_index("user_id", unique=True)
        await db["leaderboard"].create_index("total_score")
        logger.info("✅ Created leaderboard collection with indexes")
        
        # Insert sample data only if collections are empty
        users_count = await db["users"].count_documents({})
        if users_count == 0:
            sample_users = [
                {
                    "id": "user-1",
                    "name": "Alex Johnson",
                    "email": "alex@pixelpirates.com",
                    "password": "hashed_password_123",  # In real app this would be properly hashed
                    "completedTopics": ["topic-1"],
                    "pendingTopics": ["topic-3", "topic-4", "topic-5"],
                    "inProgressTopics": ["topic-2"],
                    "videosWatched": [],
                    "totalScore": 85,
                    "rank": 3,
                    "preferredStyle": "visual",
                    "confusionCount": 0,
                    "createdAt": datetime.utcnow().isoformat(),
                    "updatedAt": datetime.utcnow().isoformat()
                },
                {
                    "id": "user-2", 
                    "name": "Sarah Johnson",
                    "email": "sarah@pixelpirates.com",
                    "password": "hashed_password_456",
                    "completedTopics": ["topic-1", "topic-2"],
                    "pendingTopics": ["topic-5"],
                    "inProgressTopics": ["topic-3", "topic-4"],
                    "videosWatched": [],
                    "totalScore": 95,
                    "rank": 1,
                    "preferredStyle": "logical",
                    "confusionCount": 0,
                    "createdAt": datetime.utcnow().isoformat(),
                    "updatedAt": datetime.utcnow().isoformat()
                },
                {
                    "id": "user-3",
                    "name": "Michael Chen", 
                    "email": "michael@pixelpirates.com",
                    "password": "hashed_password_789",
                    "completedTopics": ["topic-1"],
                    "pendingTopics": ["topic-4", "topic-5"],
                    "inProgressTopics": ["topic-2", "topic-3"],
                    "videosWatched": [],
                    "totalScore": 92,
                    "rank": 2,
                    "preferredStyle": "simplified",
                    "confusionCount": 0,
                    "createdAt": datetime.utcnow().isoformat(),
                    "updatedAt": datetime.utcnow().isoformat()
                }
            ]
            
            await db["users"].insert_many(sample_users)
            logger.info(f"✅ Inserted {len(sample_users)} sample users")
        else:
            logger.info(f"ℹ️  Users collection already has {users_count} documents")
        
        # Sample topics
        topics_count = await db["topics"].count_documents({})
        if topics_count == 0:
            sample_topics = [
                {
                    "id": "topic-1",
                    "language": "Python",
                    "topicName": "Python Loops",
                    "difficulty": "Beginner",
                    "overview": "Loops are fundamental constructs in Python that allow you to execute a block of code repeatedly.",
                    "explanations": [
                        {
                            "style": "visual",
                            "title": "Visual Explanation",
                            "icon": "🎨",
                            "content": "Imagine a conveyor belt in a factory. Each item on the belt gets the same processing."
                        },
                        {
                            "style": "simplified", 
                            "title": "Simplified Explanation",
                            "icon": "📝",
                            "content": "A loop simply means 'do this thing again and again.'"
                        }
                    ],
                    "quiz": [
                        {
                            "id": "q1",
                            "question": "What is a for loop used for?",
                            "options": [
                                "Repeating code a specific number of times",
                                "Making decisions in code", 
                                "Storing data",
                                "Creating functions"
                            ],
                            "correctAnswer": 0,
                            "explanation": "A for loop is used to repeat code a specific number of times."
                        }
                    ],
                    "createdAt": datetime.utcnow().isoformat(),
                    "updatedAt": datetime.utcnow().isoformat()
                },
                {
                    "id": "topic-2",
                    "language": "Python",
                    "topicName": "Python Variables",
                    "difficulty": "Beginner",
                    "overview": "Variables are containers that store data values in Python.",
                    "explanations": [
                        {
                            "style": "visual",
                            "title": "Visual Explanation",
                            "icon": "📦",
                            "content": "Think of variables as labeled boxes where you can store different items."
                        }
                    ],
                    "quiz": [],
                    "createdAt": datetime.utcnow().isoformat(),
                    "updatedAt": datetime.utcnow().isoformat()
                }
            ]
            
            await db["topics"].insert_many(sample_topics)
            logger.info(f"✅ Inserted {len(sample_topics)} sample topics")
        else:
            logger.info(f"ℹ️  Topics collection already has {topics_count} documents")
            
        # Validation
        logger.info("🔍 Validating database setup...")
        
        collections = await db.list_collection_names()
        logger.info(f"📋 Available collections: {collections}")
        
        users_count = await db["users"].count_documents({})
        topics_count = await db["topics"].count_documents({})
        
        logger.info(f"👤 Users in database: {users_count}")
        logger.info(f"📚 Topics in database: {topics_count}")
        
        # Test a sample query
        sample_user = await db["users"].find_one({"email": "alex@pixelpirates.com"})
        if sample_user:
            logger.info(f"✅ Sample query successful - found user: {sample_user['name']}")
        
        # Close connection
        client.close()
        logger.info("✅ MongoDB connection closed successfully")
        
        logger.info("\n🎉 MongoDB database initialization completed successfully!")
        logger.info("🔗 Your MongoDB is ready with:")
        logger.info("   • Proper indexes for performance")
        logger.info("   • Sample users and topics")
        logger.info("   • All required collections")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(simple_init_database())
    
    if success:
        print("\n✅ SUCCESS: MongoDB is perfectly set up and ready to use!")
        print("🔗 Connection: mongodb://localhost:27017/")
        print("🗄️  Database: pixel_pirates")
    else:
        print("\n❌ FAILED: Database initialization encountered errors")