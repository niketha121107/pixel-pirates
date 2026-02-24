"""
MongoDB Database Initialization Script

This script initializes the MongoDB database with:
1. Creates necessary collections
2. Sets up indexes for better performance  
3. Inserts sample data if collections are empty
4. Validates the database setup
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import Settings
from app.core.database import connect_to_mongo, get_database, Collections
from app.core.auth import hash_password
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_indexes():
    """Create database indexes for better performance"""
    try:
        db = await get_database()
        
        # Users collection indexes
        await db[Collections.USERS].create_index("email", unique=True)
        await db[Collections.USERS].create_index("id", unique=True)
        logger.info("✅ Created indexes for users collection")
        
        # Topics collection indexes
        await db[Collections.TOPICS].create_index("id", unique=True)
        await db[Collections.TOPICS].create_index([("language", 1), ("difficulty", 1)])
        logger.info("✅ Created indexes for topics collection")
        
        # User Progress collection indexes
        await db[Collections.USER_PROGRESS].create_index([("user_id", 1), ("topic_id", 1)], unique=True)
        await db[Collections.USER_PROGRESS].create_index("user_id")
        logger.info("✅ Created indexes for user_progress collection")
        
        # Quizzes collection indexes
        await db[Collections.QUIZZES].create_index("id", unique=True)
        await db[Collections.QUIZZES].create_index("topic_id")
        logger.info("✅ Created indexes for quizzes collection")
        
        # Videos collection indexes
        await db[Collections.VIDEOS].create_index("id", unique=True)
        await db[Collections.VIDEOS].create_index("youtube_id", unique=True)
        await db[Collections.VIDEOS].create_index([("language", 1), ("topic", 1)])
        logger.info("✅ Created indexes for videos collection")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating indexes: {e}")
        return False

async def insert_sample_data():
    """Insert sample data if collections are empty"""
    try:
        db = await get_database()
        
        # Sample users
        users_count = await db[Collections.USERS].count_documents({})
        if users_count == 0:
            sample_users = [
                {
                    "id": "user-1",
                    "name": "Alex Johnson",
                    "email": "alex@pixelpirates.com",
                    "password": hash_password("password123"),
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
                    "password": hash_password("password456"),
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
                    "password": hash_password("password789"),
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
            
            await db[Collections.USERS].insert_many(sample_users)
            logger.info(f"✅ Inserted {len(sample_users)} sample users")
        
        # Sample topics
        topics_count = await db[Collections.TOPICS].count_documents({})
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
                    "quiz": [],
                    "createdAt": datetime.utcnow().isoformat(),
                    "updatedAt": datetime.utcnow().isoformat()
                }
            ]
            
            await db[Collections.TOPICS].insert_many(sample_topics)
            logger.info(f"✅ Inserted {len(sample_topics)} sample topics")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Error inserting sample data: {e}")
        return False

async def validate_database():
    """Validate that the database is properly set up"""
    try:
        db = await get_database()
        
        # Check collections exist and have data
        collections = await db.list_collection_names()
        logger.info(f"📋 Available collections: {collections}")
        
        # Check users
        users_count = await db[Collections.USERS].count_documents({})
        logger.info(f"👤 Users in database: {users_count}")
        
        # Check topics
        topics_count = await db[Collections.TOPICS].count_documents({})
        logger.info(f"📚 Topics in database: {topics_count}")
        
        # Test a sample query
        sample_user = await db[Collections.USERS].find_one({"email": "alex@pixelpirates.com"})
        if sample_user:
            logger.info("✅ Sample query successful - found test user")
        else:
            logger.warning("⚠️  Sample query failed - test user not found")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Database validation failed: {e}")
        return False

async def initialize_database():
    """Complete database initialization"""
    logger.info("🚀 Starting MongoDB database initialization...")
    
    settings = Settings()
    
    # Connect to MongoDB
    success = await connect_to_mongo(settings) 
    if not success:
        logger.error("❌ Failed to connect to MongoDB")
        return False
    
    # Create indexes
    indexes_created = await create_indexes()
    if not indexes_created:
        logger.error("❌ Failed to create indexes")
        return False
        
    # Insert sample data
    data_inserted = await insert_sample_data()
    if not data_inserted:
        logger.error("❌ Failed to insert sample data") 
        return False
        
    # Validate setup
    validation_passed = await validate_database()
    if not validation_passed:
        logger.error("❌ Database validation failed")
        return False
        
    logger.info("✅ MongoDB database initialization completed successfully!")
    return True

if __name__ == "__main__":
    asyncio.run(initialize_database())