#!/usr/bin/env python3
"""
Fetch highly recommended YouTube videos for all topics
Uses YouTube Data API v3
"""

import os
import sys
from datetime import datetime
from googleapiclient.discovery import build
from pymongo import MongoClient
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load YouTube API key
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "AIzaSyA3_26DIrG1LvgJEAlhr05QXcB-tFks4Mc")

# MongoDB config
MONGO_URL = "mongodb://localhost:27017/"
DB_NAME = "pixel_pirates"
TOPICS_COLLECTION = "topics"
VIDEOS_COLLECTION = "videos"

class YouTubeVideoFetcher:
    """Fetch and recommend YouTube videos for topics"""
    
    def __init__(self, api_key):
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.mongo_client = MongoClient(MONGO_URL)
        self.db = self.mongo_client[DB_NAME]
        
    def search_videos(self, topic_name, max_results=10):
        """
        Search YouTube for videos related to a topic
        Returns highly recommended videos (based on views, likes, relevance)
        """
        try:
            logger.info(f"🔍 Searching YouTube for: {topic_name}")
            
            # Search query combining topic name with educational keywords
            query = f"{topic_name} tutorial educational"
            
            request = self.youtube.search().list(
                q=query,
                type='video',
                part='id,snippet',
                maxResults=max_results,
                order='relevance',  # Most relevant first
                safeSearch='strict',
                regionCode='US',
                videoDuration='medium'  # 4-20 minutes
            )
            
            search_results = request.execute()
            videos = []
            
            for item in search_results.get('items', []):
                video_id = item['id']['videoId']
                
                # Get detailed video stats (views, likes, etc.)
                video_details = self._get_video_stats(video_id)
                
                videos.append({
                    'videoId': video_id,
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'thumbnail': item['snippet']['thumbnails'].get('high', {}).get('url'),
                    'channel': item['snippet']['channelTitle'],
                    'publishedAt': item['snippet']['publishedAt'],
                    'views': video_details.get('views', 0),
                    'likes': video_details.get('likes', 0),
                    'duration': video_details.get('duration', ''),
                    'score': self._calculate_video_score(video_details)
                })
            
            # Sort by recommendation score
            videos.sort(key=lambda x: x['score'], reverse=True)
            
            logger.info(f"   ✓ Found {len(videos)} videos for: {topic_name}")
            return videos[:5]  # Return top 5 recommended
            
        except Exception as e:
            logger.error(f"   ✗ Error searching YouTube for {topic_name}: {e}")
            return []
    
    def _get_video_stats(self, video_id):
        """Get detailed stats for a video"""
        try:
            request = self.youtube.videos().list(
                id=video_id,
                part='statistics,contentDetails'
            )
            
            response = request.execute()
            
            if response['items']:
                stats = response['items'][0].get('statistics', {})
                content = response['items'][0].get('contentDetails', {})
                
                return {
                    'views': int(stats.get('viewCount', 0)),
                    'likes': int(stats.get('likeCount', 0)),
                    'duration': content.get('duration', '')
                }
        except Exception as e:
            logger.debug(f"Could not fetch stats for video {video_id}: {e}")
        
        return {'views': 0, 'likes': 0, 'duration': ''}
    
    def _calculate_video_score(self, video_stats):
        """
        Calculate recommendation score based on:
        - View count (weight: 60%)
        - Like count (weight: 40%)
        """
        views = video_stats.get('views', 0)
        likes = video_stats.get('likes', 0)
        
        # Normalize scores (log scale to handle large numbers)
        view_score = min(100, (views / 1000000) * 50) if views > 0 else 0
        like_score = min(100, (likes / 100000) * 50) if likes > 0 else 0
        
        # Combined score (0-100)
        score = (view_score * 0.6) + (like_score * 0.4)
        return score
    
    def get_all_topics(self):
        """Get all topics from MongoDB"""
        try:
            topics = list(self.db[TOPICS_COLLECTION].find({}))
            logger.info(f"📚 Loaded {len(topics)} topics from MongoDB")
            return topics
        except Exception as e:
            logger.error(f"Error loading topics: {e}")
            return []
    
    def save_videos(self, topic_id, topic_name, videos):
        """Save videos to MongoDB"""
        try:
            # Update topic with videos
            self.db[TOPICS_COLLECTION].update_one(
                {"_id": topic_id},
                {
                    "$set": {
                        "videos": videos,
                        "lastVideoUpdate": datetime.now().isoformat(),
                        "videoSearchQuery": f"{topic_name} tutorial educational"
                    }
                }
            )
            
            logger.info(f"   ✓ Saved {len(videos)} videos to topic: {topic_name}")
            return True
        except Exception as e:
            logger.error(f"   ✗ Error saving videos: {e}")
            return False
    
    def process_all_topics(self):
        """Process all topics and fetch their videos"""
        topics = self.get_all_topics()
        
        if not topics:
            logger.error("No topics found!")
            return False
        
        successful = 0
        failed = 0
        
        logger.info(f"🚀 Starting to fetch videos for {len(topics)} topics...\n")
        
        for i, topic in enumerate(topics, 1):
            topic_id = topic.get("_id")
            topic_name = topic.get("topicName") or topic.get("name", "Unknown")
            
            logger.info(f"[{i}/{len(topics)}] Processing: {topic_name}")
            
            # Fetch videos from YouTube
            videos = self.search_videos(topic_name)
            
            if videos:
                # Save to MongoDB
                if self.save_videos(topic_id, topic_name, videos):
                    successful += 1
                    
                    # Display top recommendation
                    top_video = videos[0]
                    logger.info(f"   ⭐ Top recommendation: {top_video['title']}")
                    logger.info(f"      Views: {top_video['views']:,} | Score: {top_video['score']:.2f}")
                else:
                    failed += 1
            else:
                logger.warning(f"   ⚠ No videos found for: {topic_name}")
                failed += 1
            
            logger.info("")  # Blank line for readability
        
        # Print summary
        logger.info("=" * 70)
        logger.info(f"✅ COMPLETED: {successful} topics with videos")
        logger.info(f"❌ FAILED: {failed} topics")
        logger.info(f"📊 Success rate: {(successful/len(topics)*100):.1f}%")
        logger.info("=" * 70)
        
        return successful > 0

def main():
    """Main execution"""
    logger.info("=" * 70)
    logger.info("🎬 YouTube Video Fetcher for Pixel Pirates")
    logger.info(f"YouTube API Key: {YOUTUBE_API_KEY[:20]}...")
    logger.info("=" * 70 + "\n")
    
    fetcher = YouTubeVideoFetcher(YOUTUBE_API_KEY)
    
    try:
        success = fetcher.process_all_topics()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
