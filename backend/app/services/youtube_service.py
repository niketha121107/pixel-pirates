from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Any, Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class YouTubeService:
    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY
        self.youtube = build(
            settings.YOUTUBE_API_SERVICE_NAME, 
            settings.YOUTUBE_API_VERSION, 
            developerKey=self.api_key
        )
    
    async def search_videos(
        self, 
        query: str, 
        max_results: int = 10,
        duration: str = "medium",
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """Search for educational videos on YouTube"""
        try:
            # Enhanced search query for educational content
            enhanced_query = f"{query} tutorial programming learn code explanation"
            
            # Duration filter mapping
            duration_filter = {
                "short": "short",    # < 4 minutes
                "medium": "medium",  # 4-20 minutes  
                "long": "long"       # > 20 minutes
            }.get(duration, "medium")
            
            search_response = self.youtube.search().list(
                q=enhanced_query,
                part="id,snippet",
                maxResults=max_results,
                type="video",
                videoDuration=duration_filter,
                videoEmbeddable="true",
                videoSyndicated="true",
                relevanceLanguage=language,
                safeSearch="strict",
                order="relevance"
            ).execute()
            
            video_ids = []
            for item in search_response["items"]:
                video_ids.append(item["id"]["videoId"])
            
            # Get video details including duration
            videos_response = self.youtube.videos().list(
                part="contentDetails,statistics,snippet",
                id=",".join(video_ids)
            ).execute()
            
            videos = []
            for item in videos_response["items"]:
                video_data = {
                    "id": f"yt_{item['id']}",
                    "title": item["snippet"]["title"],
                    "language": self._extract_language_from_query(query),
                    "youtubeId": item["id"],
                    "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                    "duration": self._format_duration(item["contentDetails"]["duration"]),
                    "description": item["snippet"]["description"][:200] + "..." if len(item["snippet"]["description"]) > 200 else item["snippet"]["description"],
                    "channelTitle": item["snippet"]["channelTitle"],
                    "viewCount": int(item["statistics"].get("viewCount", 0)),
                    "publishedAt": item["snippet"]["publishedAt"],
                    "relevanceScore": self._calculate_relevance_score(item, query)
                }
                videos.append(video_data)
            
            # Sort by relevance score
            videos.sort(key=lambda x: x["relevanceScore"], reverse=True)
            return videos
            
        except HttpError as e:
            logger.error(f"YouTube API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in YouTube search: {e}")
            return []
    
    async def get_video_details(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific video"""
        try:
            response = self.youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            ).execute()
            
            if not response["items"]:
                return None
                
            item = response["items"][0]
            return {
                "id": f"yt_{item['id']}",
                "title": item["snippet"]["title"],
                "youtubeId": item["id"],
                "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
                "duration": self._format_duration(item["contentDetails"]["duration"]),
                "description": item["snippet"]["description"],
                "channelTitle": item["snippet"]["channelTitle"],
                "viewCount": int(item["statistics"].get("viewCount", 0)),
                "likeCount": int(item["statistics"].get("likeCount", 0)),
                "publishedAt": item["snippet"]["publishedAt"]
            }
            
        except HttpError as e:
            logger.error(f"YouTube API error getting video details: {e}")
            return None
    
    def _format_duration(self, duration: str) -> str:
        """Convert ISO 8601 duration to readable format"""
        import re
        
        # Parse PT15M33S format
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if not match:
            return "0:00"
        
        hours, minutes, seconds = match.groups()
        hours = int(hours) if hours else 0
        minutes = int(minutes) if minutes else 0
        seconds = int(seconds) if seconds else 0
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    def _extract_language_from_query(self, query: str) -> str:
        """Extract programming language from search query"""
        languages = {
            "python": "Python",
            "java": "Java", 
            "javascript": "JavaScript",
            "js": "JavaScript",
            "c++": "C++",
            "cpp": "C++",
            "c": "C",
            "sql": "SQL",
            "html": "HTML",
            "css": "CSS",
            "react": "React",
            "node": "Node.js",
            "php": "PHP",
            "go": "Go",
            "rust": "Rust",
            "swift": "Swift",
            "kotlin": "Kotlin"
        }
        
        query_lower = query.lower()
        for key, value in languages.items():
            if key in query_lower:
                return value
        
        return "Programming"
    
    def _calculate_relevance_score(self, video_item: Dict, query: str) -> int:
        """Calculate relevance score based on various factors"""
        score = 100
        
        title = video_item["snippet"]["title"].lower()
        description = video_item["snippet"]["description"].lower()
        query_lower = query.lower()
        
        # Title match bonus
        if query_lower in title:
            score += 50
        
        # Description match bonus
        if query_lower in description:
            score += 20
            
        # Educational keywords bonus
        educational_keywords = ["tutorial", "learn", "course", "guide", "beginner", "explained"]
        for keyword in educational_keywords:
            if keyword in title or keyword in description:
                score += 10
        
        # View count factor (more views = higher quality usually)
        view_count = int(video_item["statistics"].get("viewCount", 0))
        if view_count > 100000:
            score += 30
        elif view_count > 10000:
            score += 15
        
        return score

# Global instance
youtube_service = YouTubeService()