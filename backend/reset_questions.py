#!/usr/bin/env python3
"""
Reset all questions and reseed with corrected version
"""

import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings


async def reset_questions():
    """Remove quiz field from all topics"""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DATABASE]
    topics_collection = db["topics"]
    
    print("🗑️  Cleaning up old questions...")
    result = await topics_collection.update_many(
        {},
        {"$unset": {"quiz": ""}}
    )
    
    print(f"✅ Removed questions from {result.modified_count} topics")
    client.close()


if __name__ == "__main__":
    asyncio.run(reset_questions())
