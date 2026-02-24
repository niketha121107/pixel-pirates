from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import asyncio
from app.models import Video, WatchedVideo, SuccessResponse
from app.data import get_user_by_id, add_watched_video, MOCK_USERS
from app.services.youtube_service import youtube_service
from app.core.auth import get_current_user_from_token

router = APIRouter()

class VideoWatchRequest(BaseModel):
    video_id: str
    youtube_id: str
    title: str
    duration: str
    time_watched: str
    language: Optional[str] = "Programming"

@router.get("/search", response_model=SuccessResponse)
async def search_videos(
    q: str = Query(..., description="Search query for videos"),
    language: Optional[str] = Query(None, description="Programming language filter"),
    duration: str = Query("medium", description="Video duration preference: short, medium, long"),
    limit: int = Query(10, ge=1, le=20, description="Maximum number of results")
):
    """Search for educational videos using YouTube API"""
    try:
        # Enhance query with programming context if language specified
        search_query = f"{q} {language}" if language else q
        
        videos = await youtube_service.search_videos(
            query=search_query,
            max_results=limit,
            duration=duration
        )
        
        return SuccessResponse(
            success=True,
            message=f"Found {len(videos)} videos for '{q}'",
            data={
                "query": q,
                "language": language,
                "totalResults": len(videos),
                "videos": videos
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching videos: {str(e)}"
        )

@router.get("/recommendations", response_model=SuccessResponse)
async def get_video_recommendations(
    current_user: dict = Depends(get_current_user_from_token),
    limit: int = Query(5, ge=1, le=10, description="Number of recommendations")
):
    """Get personalized video recommendations based on user's learning progress"""
    user = current_user
    
    try:
        recommendations = []
        
        # Get recommendations based on pending and in-progress topics
        pending_topics = user.get("pendingTopics", [])
        in_progress_topics = user.get("inProgressTopics", [])
        
        # Mock topic names - in production, you'd get these from the topics data
        topic_names = {
            "topic-1": "Python Loops",
            "topic-2": "Java OOP Basics", 
            "topic-3": "Data Structures",
            "topic-4": "Algorithms",
            "topic-5": "SQL Joins"
        }
        
        # Search for videos related to user's current learning path
        search_topics = []
        for topic_id in (in_progress_topics + pending_topics)[:3]:
            if topic_id in topic_names:
                search_topics.append(topic_names[topic_id])
        
        # If no specific topics, recommend general programming videos
        if not search_topics:
            search_topics = ["Programming fundamentals", "Code tutorial beginner"]
        
        for topic in search_topics[:2]:  # Limit to 2 topics to avoid too many API calls
            videos = await youtube_service.search_videos(
                query=topic,
                max_results=3,
                duration="medium"
            )
            recommendations.extend(videos[:2])  # Take top 2 from each topic
        
        # Remove duplicates and limit results
        seen_ids = set()
        unique_recommendations = []
        for video in recommendations:
            if video["youtubeId"] not in seen_ids and len(unique_recommendations) < limit:
                seen_ids.add(video["youtubeId"])
                unique_recommendations.append(video)
        
        return SuccessResponse(
            success=True,
            message="Video recommendations generated",
            data={
                "recommendations": unique_recommendations,
                "basedOn": search_topics,
                "totalRecommendations": len(unique_recommendations)
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting recommendations: {str(e)}"
        )

@router.get("/watched", response_model=SuccessResponse)
async def get_watched_videos(current_user: dict = Depends(get_current_user_from_token)):
    """Get user's watched video history"""
    user = current_user
    
    watched_videos = user.get("videosWatched", [])
    
    return SuccessResponse(
        success=True,
        message="Watched videos retrieved successfully",
        data={
            "watchedVideos": watched_videos,
            "totalWatched": len(watched_videos)
        }
    )

@router.post("/watch", response_model=SuccessResponse)
async def mark_video_watched(
    watch_request: VideoWatchRequest,
    current_user: dict = Depends(get_current_user_from_token)
):
    """Mark a video as watched by the user"""
    user = current_user
    
    # Create watched video entry
    watched_video = {
        "id": watch_request.video_id,
        "title": watch_request.title,
        "language": watch_request.language,
        "youtubeId": watch_request.youtube_id,
        "thumbnail": f"https://img.youtube.com/vi/{watch_request.youtube_id}/mqdefault.jpg",
        "duration": watch_request.duration,
        "watchedAt": "2026-02-24",  # In production, use actual timestamp
        "timeWatched": watch_request.time_watched
    }
    
    success = add_watched_video(current_user["id"], watched_video)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save watched video"
        )
    
    return SuccessResponse(
        success=True,
        message="Video marked as watched",
        data={"watchedVideo": watched_video}
    )

@router.get("/{video_id}/details", response_model=SuccessResponse)
async def get_video_details(video_id: str):
    """Get detailed information about a specific YouTube video"""
    try:
        # Extract YouTube ID from our video ID format
        youtube_id = video_id.replace("yt_", "") if video_id.startswith("yt_") else video_id
        
        try:
            video_details = await asyncio.wait_for(
                youtube_service.get_video_details(youtube_id), timeout=10.0
            )
        except asyncio.TimeoutError:
            video_details = None
        
        if not video_details:
            raise HTTPException(status_code=404, detail="Video not found")
        
        return SuccessResponse(
            success=True,
            message="Video details retrieved successfully",
            data={"video": video_details}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting video details: {str(e)}"
        )

@router.get("/trending/{language}", response_model=SuccessResponse)
async def get_trending_videos_by_language(
    language: str,
    limit: int = Query(10, ge=1, le=20, description="Number of trending videos")
):
    """Get trending educational videos for a specific programming language"""
    try:
        async def _fetch_trending():
            # Search for current/popular topics in the language
            trending_queries = [
                f"{language} tutorial 2026",
                f"{language} advanced concepts",
            ]
            
            all_videos = []
            for query in trending_queries:
                videos = await youtube_service.search_videos(
                    query=query,
                    max_results=5,
                    duration="medium"
                )
                all_videos.extend(videos)
            return all_videos
        
        try:
            all_videos = await asyncio.wait_for(_fetch_trending(), timeout=15.0)
        except asyncio.TimeoutError:
            all_videos = []
        
        # Remove duplicates and sort by relevance + view count
        seen_ids = set()
        unique_videos = []
        for video in all_videos:
            if video["youtubeId"] not in seen_ids:
                seen_ids.add(video["youtubeId"])
                unique_videos.append(video)
        
        # Sort by view count and relevance score
        unique_videos.sort(
            key=lambda x: (x.get("viewCount", 0), x.get("relevanceScore", 0)), 
            reverse=True
        )
        
        return SuccessResponse(
            success=True,
            message=f"Trending {language} videos retrieved",
            data={
                "language": language,
                "trendingVideos": unique_videos[:limit],
                "totalFound": len(unique_videos)
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting trending videos: {str(e)}"
        )