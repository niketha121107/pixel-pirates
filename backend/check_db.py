import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check():
    db = AsyncIOMotorClient('mongodb://localhost:27017/')['pixel_pirates']
    fallbacks = await db.topics.count_documents({'videos.youtubeId': 'rfscVS0vtik'})
    all_videos = await db.topics.count_documents({'videos': {'$exists': True, '$ne': []}})
    print(f"Total topics with videos: {all_videos}")
    print(f"Total topics with fallback 'rfscVS0vtik': {fallbacks}")

if __name__ == '__main__':
    asyncio.run(check())
