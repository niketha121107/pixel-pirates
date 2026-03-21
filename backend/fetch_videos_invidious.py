#!/usr/bin/env python3
"""
Fetch YouTube videos using Invidious API (no quota limits)
For remaining topics that weren't covered by the official YouTube API
"""

import requests
import logging
from pymongo import MongoClient
from datetime import datetime
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

MONGO_URL = "mongodb://localhost:27017/"
DB_NAME = "pixel_pirates"
TOPICS_COLLECTION = "topics"

# Public Invidious instances
INVIDIOUS_INSTANCES = [
    "https://yewtu.be",
    "https://invidious.io",
    "https://inv.vern.cc"
]

class InvidiousVideoFetcher:
    """Fetch videos using Invidious API (no quota limits)"""
    
    def __init__(self):
        self.mongo_client = MongoClient(MONGO_URL)
        self.db = self.mongo_client[DB_NAME]
        self.base_url = INVIDIOUS_INSTANCES[0]
    
    def search_videos(self, topic_name, max_results=10):
        """Search videos via Invidious API"""
        try:
            logger.info(f"🔍 Searching Invidious for: {topic_name}")
            
            query = f"{topic_name} tutorial educational"
            
            url = f"{self.base_url}/api/v1/search"
            params = {
                "q": query,
                "type": "video",
                "sort_by": "relevance",
                "limit": max_results
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            results = response.json()
            videos = []
            
            for item in results:
                if item.get('type') == 'video':
                    videos.append({
                        'videoId': item.get('videoId'),
                        'title': item.get('title'),
                        'description': item.get('description', ''),
                        'thumbnail': f"https://i.ytimg.com/vi/{item.get('videoId')}/hqdefault.jpg",
                        'channel': item.get('author', 'Unknown'),
                        'publishedAt': item.get('publishedDate', ''),
                        'views': item.get('viewCount', 0),
                        'duration': item.get('lengthSeconds', 0),
                        'score': self._calculate_score(item)
                    })
            
            # Sort by score
            videos.sort(key=lambda x: x['score'], reverse=True)
            logger.info(f"   ✓ Found {len(videos)} videos")
            return videos[:5]  # Top 5
            
        except Exception as e:
            logger.error(f"   ✗ Error: {e}")
            return []
    
    def _calculate_score(self, item):
        """Calculate recommendation score"""
        views = item.get('viewCount', 0)
        
        # Log scale for views
        score = min(100, (views / 1000000) * 100) if views > 0 else 0
        return score
    
    def get_topics_without_videos(self):
        """Get topics that don't have videos yet"""
        try:
            topics = list(self.db[TOPICS_COLLECTION].find(
                {"videos": {"$exists": False}}
            ).sort("_id", 1))
            
            logger.info(f"📚 Found {len(topics)} topics without videos")
            return topics
        except Exception as e:
            logger.error(f"Error: {e}")
            return []
    
    def save_videos(self, topic_id, topic_name, videos):
        """Save videos to MongoDB"""
        try:
            self.db[TOPICS_COLLECTION].update_one(
                {"_id": topic_id},
                {
                    "$set": {
                        "videos": videos,
                        "lastVideoUpdate": datetime.now().isoformat(),
                        "videoSource": "invidious"
                    }
                }
            )
            
            logger.info(f"   ✓ Saved {len(videos)} videos")
            return True
        except Exception as e:
            logger.error(f"   ✗ Save error: {e}")
            return False
    
    def process_remaining_topics(self):
        """Process topics without videos"""
        topics = self.get_topics_without_videos()
        
        if not topics:
            logger.info("✅ All topics already have videos!")
            return True
        
        successful = 0
        failed = 0
        
        logger.info(f"🚀 Fetching videos for {len(topics)} remaining topics\n")
        
        for i, topic in enumerate(topics, 1):
            topic_id = topic.get("_id")
            topic_name = topic.get("topicName") or topic.get("name", "Unknown")
            
            logger.info(f"[{i}/{len(topics)}] {topic_name}")
            
            videos = self.search_videos(topic_name)
            
            if videos:
                if self.save_videos(topic_id, topic_name, videos):
                    successful += 1
                    top = videos[0]
                    logger.info(f"   ⭐ Top: {top['title']}")
                    logger.info(f"      Views: {top['views']:,}")
                else:
                    failed += 1
            else:
                logger.warning(f"   ⚠ No videos found")
                failed += 1
            
            # Rate limiting
            time.sleep(0.5)
            logger.info("")
        
        logger.info("=" * 70)
        logger.info(f"✅ Success: {successful}")
        logger.info(f"❌ Failed: {failed}")
        logger.info(f"📊 Rate: {(successful/len(topics)*100):.1f}%")
        logger.info("=" * 70)
        
        return successful > 0

def main():
    logger.info("=" * 70)
    logger.info("🎬 Invidious Video Fetcher")
    logger.info("Processing remaining topics (quota-free method)")
    logger.info("=" * 70 + "\n")
    
    fetcher = InvidiousVideoFetcher()
    fetcher.process_remaining_topics()

if __name__ == "__main__":
    main()
