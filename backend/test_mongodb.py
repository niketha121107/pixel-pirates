"""
Simple MongoDB Connection Test Script
This script tests the MongoDB connection without FastAPI dependencies
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

async def test_mongodb_connection():
    """Test MongoDB connection"""
    print("🔍 Testing MongoDB Connection...")
    print(f"📍 Connecting to: mongodb://localhost:27017/")
    
    try:
        # Create client with timeout settings
        client = AsyncIOMotorClient(
            "mongodb://localhost:27017/",
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000
        )
        
        print("⏳ Attempting to connect...")
        
        # Test the connection
        await client.admin.command('ping')
        print("✅ MongoDB connection successful! The ping command worked.")
        
        # Get server info
        server_info = await client.server_info()
        print(f"✅ MongoDB Server Version: {server_info.get('version', 'Unknown')}")
        
        # Test database operations
        db = client["pixel_pirates"]
        print(f"✅ Connected to database: pixel_pirates")
        
        # Test collection operations
        test_collection = db["test_connection"]
        
        # Insert a test document
        test_doc = {
            "message": "MongoDB connection test",
            "timestamp": "2026-02-24",
            "status": "success"
        }
        
        result = await test_collection.insert_one(test_doc)
        print(f"✅ Test document inserted with ID: {result.inserted_id}")
        
        # Read the test document
        found_doc = await test_collection.find_one({"_id": result.inserted_id})
        print(f"✅ Test document retrieved: {found_doc['message']}")
        
        # Clean up - remove test document
        await test_collection.delete_one({"_id": result.inserted_id})
        print("✅ Test document cleaned up")
        
        # List databases
        databases = await client.list_database_names()
        print(f"📋 Available databases: {databases}")
        
        # List collections in pixel_pirates database
        collections = await db.list_collection_names()
        print(f"📋 Collections in pixel_pirates database: {collections}")
        
        # Close connection
        client.close()
        print("✅ MongoDB connection closed successfully")
        
        print("\n🎉 MongoDB Connection Test PASSED!")
        print("🔗 Your MongoDB is properly connected and working at: mongodb://localhost:27017/")
        return True
        
    except ConnectionFailure as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("\n💡 Possible solutions:")
        print("   1. Make sure MongoDB is running on your system")
        print("   2. Check if MongoDB service is started")
        print("   3. Verify MongoDB is listening on localhost:27017")
        return False
        
    except ServerSelectionTimeoutError as e:
        print(f"❌ MongoDB server selection timeout: {e}")
        print("\n💡 Possible solutions:")
        print("   1. MongoDB server is not running")
        print("   2. MongoDB is running on a different port")
        print("   3. Network connectivity issues")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    print("🚀 Starting MongoDB Connection Test...")
    print("=" * 50)
    
    success = asyncio.run(test_mongodb_connection())
    
    print("=" * 50)
    if success:
        print("🎯 Result: MongoDB connection is working perfectly!")
    else:
        print("⚠️  Result: MongoDB connection failed - please check your MongoDB setup")