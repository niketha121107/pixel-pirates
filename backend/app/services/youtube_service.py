from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Any, Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class YouTubeService:
    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY
        self._youtube = None
        self._init_failed = False

    @property
    def youtube(self):
        """Lazy-initialize YouTube client so import doesn't crash if key is bad."""
        if self._youtube is None and not self._init_failed:
            try:
                self._youtube = build(
                    settings.YOUTUBE_API_SERVICE_NAME,
                    settings.YOUTUBE_API_VERSION,
                    developerKey=self.api_key,
                )
            except Exception as e:
                logger.error(f"Failed to initialize YouTube client: {e}")
                self._init_failed = True
        return self._youtube

    async def search_for_topic(self, topic_name: str, language: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search YouTube for videos STRICTLY related to a specific topic.
        Handles compound topics like 'history and philosophy in python' by ensuring all parts are covered.
        Returns ONLY videos that are directly related to the topic - NO unrelated content.
        Falls back to Invidious if YouTube API quota is exceeded or no videos found."""
        if not self.api_key or not self.youtube:
            logger.warning("YouTube API not available — falling back to Invidious")
            return await self.search_via_invidious(topic_name, max_results)

        # Build an optimized query for the exact topic
        # For compound topics, add relevant keywords to increase precision
        query = f"{topic_name} tutorial educational explained"
        
        logger.info(f"🔍 Searching for topic: '{topic_name}'")
        
        try:
            videos = await self.search_videos(query=query, max_results=max_results*3, duration="medium")
            
            # If YouTube API returned no videos (likely quota exceeded or API down), use Invidious
            if not videos:
                logger.warning(f"⚠️  YouTube returned no videos (likely quota exceeded) — trying Invidious fallback")
                return await self.search_via_invidious(topic_name, max_results)
            
            # STRICT filter: only videos that are actually about this topic
            filtered_videos = []
            for v in videos:
                if self._is_strictly_topic_related(v, topic_name):
                    filtered_videos.append(v)
            
            logger.info(f"Found {len(filtered_videos)}/{len(videos)} videos matching '{topic_name}'")
            
            # If strict filtering removed everything, try Invidious as backup
            if not filtered_videos:
                logger.warning(f"Strict filtering removed all videos — trying Invidious fallback")
                return await self.search_via_invidious(topic_name, max_results)
            
            return filtered_videos[:max_results]
            
        except HttpError as e:
            error_str = str(e)
            # Check if it's a quota exceeded error
            if "quotaExceeded" in error_str or "quota" in error_str.lower():
                logger.warning(f"⚠️ YouTube API QUOTA EXCEEDED — falling back to Invidious")
                return await self.search_via_invidious(topic_name, max_results)
            else:
                logger.error(f"YouTube API error: {e}")
                return await self.search_via_invidious(topic_name, max_results)
        except Exception as e:
            logger.error(f"YouTube search failed for topic '{topic_name}': {e}")
            # Try Invidious fallback on any error
            return await self.search_via_invidious(topic_name, max_results)

    def _is_strictly_topic_related(self, video: Dict, topic: str) -> bool:
        """Check if a video is STRICTLY related to the topic - Handle compound topics like 'history and philosophy in python'.
        For multi-part topics, ensure most major components are covered (in title or description)."""
        title = video["title"].lower()
        description = video["description"].lower()
        topic_lower = topic.lower()
        
        logger.info(f"Checking video: '{video['title'][:60]}' against topic: '{topic}'")
        
        # ===== STEP 1: Extract meaningful words from topic =====
        # Filter out connecting words like "and", "in", "of", "the", etc.
        stop_words = {"and", "or", "in", "of", "the", "a", "an", "is", "to", "for", "with", "by"}
        topic_words = [w.strip() for w in topic_lower.split() if len(w.strip()) > 2 and w.lower() not in stop_words]
        
        logger.debug(f"  Topic keywords: {topic_words}")
        
        # ===== STEP 2: For compound topics, use smart keyword prioritization =====
        # Identify most specific/technical word as primary
        # Technical keywords like language names, specific concepts should be primary
        
        is_compound_topic = len(topic_words) > 2
        content = f"{title} {description}"
        
        if is_compound_topic:
            logger.debug(f"  Compound topic detected ({len(topic_words)} parts)")
            
            # Technical keywords that are usually more specific than generic words
            # These words identify the actual subject matter
            technical_keywords = {
                # Programming languages
                "python": 10, "javascript": 10, "java": 10, "cpp": 10, "csharp": 10,
                "ruby": 10, "golang": 10, "rust": 10, "typescript": 10, "kotlin": 10,
                "php": 10, "swift": 10, "scala": 10, "perl": 10, "dart": 10,
                # Data/concepts
                "async": 8, "await": 8, "promise": 8, "callback": 8, "concurrency": 8,
                "database": 8, "sql": 8, "mongodb": 8, "redis": 8, "api": 8,
                "rest": 8, "graphql": 8, "websocket": 8, "react": 8, "angular": 8,
                "vue": 8, "nodejs": 8, "django": 8, "flask": 8, "fastapi": 8,
                "docker": 8, "kubernetes": 8, "microservice": 8, "serverless": 8,
                # Generic but important
                "data": 5, "structure": 5, "algorithm": 5, "pattern": 5, "framework": 5,
                "library": 5, "tool": 5, "test": 5, "deploy": 5, "cloud": 5,
            }
            
            # Score each keyword by its technical importance
            word_scores = {}
            for word in topic_words:
                word_scores[word] = technical_keywords.get(word, 1)
            
            # Primary = highest scoring word (most specific)
            primary_keyword = max(topic_words, key=lambda w: word_scores.get(w, 1))
            secondary_keywords = [w for w in topic_words if w != primary_keyword]
            
            logger.debug(f"    Primary (most specific): '{primary_keyword}', Secondary: {secondary_keywords}")
            
            # PRIMARY keyword must be in title (very strict for the main topic)
            if primary_keyword not in title:
                logger.debug(f"    Primary keyword '{primary_keyword}' not in title - REJECTED")
                return False
            
            # ALL secondary keywords must be present (in title OR description combined)
            # This ensures compound topics are EXACTLY matched
            # Examples:
            # - "history and philosophy in python" → must have python (title), history AND philosophy (anywhere)
            # - "data structures and algorithms" → must have python+data+structures+algorithms
            # - "javascript async programming" → must have javascript+async+programming
            
            if len(secondary_keywords) == 0:
                # Only primary keyword - allow it
                logger.debug(f"    Single keyword topic - primary keyword present")
                return True
            
            # Count secondary keywords present
            secondary_matches = sum(1 for kw in secondary_keywords if kw in content)
            required_secondary_matches = len(secondary_keywords)  # Require ALL secondary keywords
            
            logger.debug(f"    Secondary keywords: Found {secondary_matches}/{len(secondary_keywords)}, Need all {required_secondary_matches}")
            
            if secondary_matches < required_secondary_matches:
                missing = [kw for kw in secondary_keywords if kw not in content]
                logger.debug(f"    Missing: {missing} - REJECTED")
                return False
                
            logger.debug(f"    Compound topic APPROVED - all keywords found")
        else:
            # Simple topic: at least one keyword should be present (in title or description is OK)
            content = f"{title} {description}"
            title_matches = sum(1 for word in topic_words if word in title)
            content_matches = sum(1 for word in topic_words if word in content)
            
            if content_matches == 0:
                logger.debug(f"  ❌ REJECTED: No topic keywords found: {topic_words}")
                return False
            
            if title_matches == 0:
                logger.debug(f"  ⚠️  Topic not in title, but found in description (OK for simple topics)")
        
        # ===== STEP 3: Reject entertainment/music/unrelated content =====
        reject_keywords = [
            "music", "song", "vlog", "prank", "reaction", "meme", "funny", 
            "comedy", "entertainment", "viral", "trending", "fail", "clickbait",
            "leak", "exposed", "destroyed", "crushed", "owned", "official video"
        ]
        
        for keyword in reject_keywords:
            if keyword in title or keyword in description:
                logger.debug(f"  ❌ REJECTED: Entertainment keyword '{keyword}' found")
                return False
        
        # ===== STEP 4: Require educational indicators =====
        education_keywords = [
            "tutorial", "learn", "guide", "explanation", "how to", 
            "course", "beginner", "programming", "code", "development",
            "explained", "teaching", "lesson", "fundamentals", "intro",
            "understanding", "dive", "deep dive", "masterclass",
            "lecture", "talk", "workshop", "getting started", "introduction"
        ]
        
        has_education = any(kw in title or kw in description for kw in education_keywords)
        
        if not has_education:
            logger.debug(f"  ❌ REJECTED: No educational indicators found")
            return False
        
        logger.info(f"  ✅ APPROVED topic match: '{video['title'][:60]}'")
        return True

    async def search_videos(
        self, 
        query: str, 
        max_results: int = 10,
        duration: str = "medium",
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """Search for educational videos on YouTube - WITH STRICT TOPIC FILTERING"""
        if not self.youtube:
            logger.warning("YouTube client not available")
            return []

        try:
            # Build very specific search query for exact topic
            # Include "tutorial" to prioritize educational content
            enhanced_query = f"{query} tutorial educational"
            
            logger.info(f"🔍 Searching YouTube: '{enhanced_query}'")
            
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
                order="relevance",
                regionCode="US"
            ).execute()
            
            video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
            
            if not video_ids:
                logger.warning(f"No videos found for: {enhanced_query}")
                return []
            
            logger.info(f"Found {len(video_ids)} videos - fetching details...")
            
            # Get video details including duration and statistics
            videos_response = self.youtube.videos().list(
                part="contentDetails,statistics,snippet",
                id=",".join(video_ids)
            ).execute()
            
            videos = []
            for item in videos_response.get("items", []):
                try:
                    view_count = int(item["statistics"].get("viewCount", 0))
                    like_count = int(item["statistics"].get("likeCount", 0))
                    
                    # Skip videos with very low views (likely poor quality/spam)
                    if view_count < 500:
                        logger.debug(f"⏭️  Skipping (low views): {item['snippet']['title'][:50]}")
                        continue
                    
                    video_data = {
                        "id": f"yt_{item['id']}",
                        "title": item["snippet"]["title"],
                        "language": language,
                        "youtubeId": item["id"],
                        "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                        "duration": self._format_duration(item["contentDetails"]["duration"]),
                        "description": item["snippet"]["description"][:300],
                        "channelTitle": item["snippet"]["channelTitle"],
                        "viewCount": view_count,
                        "likeCount": like_count,
                        "engagementRate": round((like_count / view_count * 100), 1) if view_count > 0 else 0,
                        "publishedAt": item["snippet"]["publishedAt"],
                        "relevanceScore": self._calculate_relevance_score(item, query)
                    }
                    videos.append(video_data)
                except Exception as e:
                    logger.warning(f"Error processing video: {e}")
                    continue
            
            # Sort by relevance score (highest first)
            videos.sort(key=lambda x: x["relevanceScore"], reverse=True)
            
            logger.info(f"✅ Returning {len(videos)} videos for '{query}'")
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
        """Calculate relevance score - STRICT topic matching only."""
        score = 0
        
        title = video_item["snippet"]["title"].lower()
        description = video_item["snippet"]["description"].lower()
        query_lower = query.lower()
        
        # Get query terms (exclude common words)
        query_terms = [w for w in query_lower.split() if len(w) > 2 and w not in ["and", "or", "the", "for"]]
        
        # ===== TITLE MATCH (CRITICAL) =====
        # Each query term in title = +100 points
        for term in query_terms:
            if term in title:
                score += 100
                logger.debug(f"  +100 for '{term}' in title")
        
        # Title must have substantial match
        if score < 100:
            logger.debug(f"  SCORE TOO LOW ({score}): Poor title match")
            score -= 500  # Massive penalty for poor topic match
        
        # ===== DESCRIPTION MATCH =====
        description_match_count = sum(1 for term in query_terms if term in description)
        score += description_match_count * 50
        
        # ===== EDUCATIONAL INDICATORS =====
        education_keywords = ["tutorial", "learn", "guide", "explained", "beginner",
                             "course", "lesson", "fundamentals", "how to", "step by step"]
        edu_count = sum(1 for kw in education_keywords if kw in title or kw in description)
        score += edu_count * 20
        
        # Minimum education requirement
        if edu_count == 0:
            score -= 300  # Massive penalty for not educational
        
        # ===== REJECT: Entertainment/Non-Educational =====
        reject_list = ["music video", "official video", "song", "prank", "reaction",
                      "vlog", "entertainment", "viral", "meme", "comedy"]
        for bad_kw in reject_list:
            if bad_kw in title or bad_kw in description:
                score -= 1000  # Instant disqualification
                logger.debug(f"  -1000 for entertainment: '{bad_kw}'")
        
        # ===== QUALITY FACTORS =====
        views = int(video_item["statistics"].get("viewCount", 0))
        likes = int(video_item["statistics"].get("likeCount", 0))
        
        # High view count (quality indicator)
        if views > 100000:
            score += 30
        elif views > 10000:
            score += 15
        elif views < 1000:
            score -= 50  # Suspicious - too few views
        
        # Engagement rate
        engagement = (likes / views * 100) if views > 0 else 0
        if engagement > 5:
            score += 20
        elif engagement < 0.5:
            score -= 20  # Suspicious engagement
        
        logger.debug(f"  Final score: {score} | Views: {views:,} | Engagement: {engagement:.1f}%")
        return score

    async def search_via_invidious(self, topic_name: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Fallback: Search YouTube videos via Invidious API (no quota limits)"""
        import httpx
        
        # List of public Invidious instances (more reliable ones)
        invidious_instances = [
            "https://invidious.kavin.rocks",
            "https://yewtu.be",
            "https://inv.vern.cc",
            "https://invidious.fdn.fr",
            "https://invidious.snopyta.org",
        ]
        
        logger.warning(f"Falling back to Invidious for: {topic_name}")
        
        query = f"{topic_name} tutorial"
        
        for instance in invidious_instances:
            try:
                logger.debug(f"  Trying Invidious instance: {instance}")
                async with httpx.AsyncClient(timeout=5) as client:
                    url = f"{instance}/api/v1/search"
                    params = {
                        "q": query,
                        "type": "video",
                        "sort_by": "relevance",
                        "limit": max_results * 2
                    }
                    
                    resp = await client.get(url, params=params)
                    if resp.status_code == 200:
                        try:
                            results = resp.json()
                            videos = []
                            
                            for item in results:
                                if item.get('type') == 'video':
                                    # Check topic relevance
                                    title = item.get('title', '').lower()
                                    if not self._is_topic_keyword_in_text(title, topic_name):
                                        continue
                                    
                                    video_id = item.get('videoId', '')
                                    if not video_id:
                                        continue
                                    
                                    videos.append({
                                        "id": f"inv_{video_id}",
                                        "title": item.get('title', 'Unknown'),
                                        "youtubeId": video_id,
                                        "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
                                        "duration": str(item.get('lengthSeconds', 0)),
                                        "description": item.get('description', '')[:300],
                                        "channelTitle": item.get('author', 'Unknown'),
                                        "viewCount": item.get('viewCount', 0),
                                        "relevanceScore": 75,
                                        "publishedAt": item.get('publishedDate', ''),
                                        "source": "invidious",
                                        "ligId": None
                                    })
                            
                            if videos:
                                logger.info(f"Success! Invidious found {len(videos)} videos from {instance}")
                                return videos[:max_results]
                        except Exception as parse_err:
                            logger.debug(f"  Parse error from {instance}: {parse_err}")
                    else:
                        logger.debug(f"  {instance} returned {resp.status_code}")
                        
            except httpx.TimeoutException:
                logger.debug(f"  {instance} timed out")
                continue
            except Exception as e:
                logger.debug(f"  {instance} error: {type(e).__name__}: {str(e)[:100]}")
                continue
        
        logger.error(f"All Invidious instances failed for: {topic_name}")
        return []

    def _is_topic_keyword_in_text(self, text: str, topic: str) -> bool:
        """Quick check if main topic keywords are in text"""
        topic_lower = topic.lower()
        stop_words = {"and", "or", "in", "of", "the", "a", "an", "is", "with"}
        
        topic_words = [w for w in topic_lower.split() if len(w) > 2 and w not in stop_words]
        
        # At least one main keyword should match
        return any(word in text for word in topic_words)

# Global instance
youtube_service = YouTubeService()