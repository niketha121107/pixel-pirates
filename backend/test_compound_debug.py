"""Debug script to see what videos are found and why they're rejected"""
import asyncio
import logging
import sys
import io
from app.services.youtube_service import YouTubeService

# Fix encoding issues on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Configure logging to be more verbose
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(message)s'
)

async def test_topic(service: YouTubeService, topic: str):
    print("\n" + "="*70)
    print(f"Testing: '{topic}'")
    print("="*70)
    
    # Get videos with minimal filtering (search_videos returns raw results)
    query = f"{topic} tutorial educational explained"
    raw_videos = await service.search_videos(query=query, max_results=15)
    
    print(f"\nRAW SEARCH RESULTS: {len(raw_videos)} videos found")
    print("-" * 70)
    
    # Show all videos found
    for i, video in enumerate(raw_videos[:10], 1):
        print(f"\n{i}. {video['title'][:70]}")
        print(f"   Channel: {video.get('channelTitle', 'Unknown')}")
        print(f"   Views: {video.get('viewCount', 'N/A'):,}")
        print(f"   Description: {video['description'][:100]}..." if video['description'] else "   Description: N/A")
        
        # Now test filtering
        is_related = service._is_strictly_topic_related(video, topic)
        if is_related:
            print(f"   OK - PASSES filtering")
        else:
            print(f"   NO - REJECTED by filtering")

async def main():
    service = YouTubeService()
    
    topics = [
        "history and philosophy in python",
        "javascript async programming",
        "python data structures and algorithms"
    ]
    
    for topic in topics:
        await test_topic(service, topic)

if __name__ == "__main__":
    asyncio.run(main())
