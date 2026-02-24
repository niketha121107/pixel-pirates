"""
MongoDB Database Connection and Utilities
"""

import asyncio
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from app.core.config import Settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None

# Create global database instance
db = Database()

async def connect_to_mongo(settings: Settings) -> bool:
    """Create database connection"""
    try:
        logger.info(f"Connecting to MongoDB at: {settings.MONGODB_URL}")
        
        # Create MongoDB client
        db.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
            maxPoolSize=10,
            minPoolSize=1
        )
        
        # Verify connection
        await db.client.admin.command('ping')
        logger.info("✅ MongoDB connection successful!")
        
        # Get database
        db.database = db.client[settings.MONGODB_DATABASE]
        logger.info(f"✅ Connected to database: {settings.MONGODB_DATABASE}")
        
        return True
        
    except ConnectionFailure as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        return False
    except ServerSelectionTimeoutError as e:
        logger.error(f"❌ MongoDB server selection timeout: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error connecting to MongoDB: {e}")
        return False

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("✅ MongoDB connection closed")

async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    if not db.database:
        raise RuntimeError("Database not initialized. Call connect_to_mongo() first.")
    return db.database

async def get_collection(collection_name: str) -> AsyncIOMotorCollection:
    """Get a specific collection"""
    database = await get_database()
    return database[collection_name]

async def test_connection() -> dict:
    """Test the database connection and return connection status"""
    try:
        if not db.client:
            return {
                "connected": False,
                "error": "No database client initialized"
            }
        
        # Test the connection
        result = await db.client.admin.command('ping')
        server_info = await db.client.server_info()
        
        # Get database stats
        db_stats = await db.database.command("dbStats")
        
        return {
            "connected": True,
            "database_name": db.database.name,
            "server_version": server_info.get("version"),
            "connection_url": "mongodb://localhost:27017/",
            "collections_count": len(await db.database.list_collection_names()),
            "database_size": db_stats.get("dataSize", 0),
            "ping_response": result
        }
        
    except Exception as e:
        return {
            "connected": False,
            "error": f"Connection test failed: {str(e)}"
        }

# Collection names for easy reference
class Collections:
    USERS = "users"
    TOPICS = "topics"
    QUIZZES = "quizzes"
    USER_PROGRESS = "user_progress"
    VIDEOS = "videos"
    LEADERBOARD = "leaderboard"
    ANALYTICS = "analytics"