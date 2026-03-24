import asyncio
import logging
import sys
from app.services.youtube_service import youtube_service

# Set up logging to stdout
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

async def test():
    print("Testing topic 'Variables in Python'...")
    videos = await youtube_service.search_for_topic("Variables in Python", "en")
    print(f"Found {len(videos)} videos:")
    for v in videos:
        print(f" - {v['title']} ({v['youtubeId']})")

asyncio.run(test())
