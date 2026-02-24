from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.models import SearchQuery, RecentSearch, SuccessResponse
from app.data import get_user_search_history, add_search_query, get_all_topics
from app.core.auth import get_current_user_from_token
import re

router = APIRouter()

class SearchRequest(BaseModel):
    query: str

@router.get("/recent", response_model=SuccessResponse)
async def get_recent_searches(current_user: dict = Depends(get_current_user_from_token)):
    """Get user's recent search history"""
    search_history = get_user_search_history(current_user["id"])
    
    return SuccessResponse(
        success=True,
        message="Recent searches retrieved successfully",
        data={"searches": search_history}
    )

@router.post("", response_model=SuccessResponse)
async def save_search_query(
    search_request: SearchRequest,
    current_user: dict = Depends(get_current_user_from_token)
):
    """Save a search query to user's history"""
    add_search_query(current_user["id"], search_request.query)
    
    return SuccessResponse(
        success=True,
        message="Search query saved",
        data={"query": search_request.query}
    )

@router.get("/suggestions", response_model=SuccessResponse)
async def get_search_suggestions(
    q: str = Query(..., description="Search query for suggestions"),
    limit: int = Query(10, ge=1, le=20, description="Maximum number of suggestions")
):
    """Get search suggestions based on partial query"""
    topics = get_all_topics()
    
    suggestions = []
    query_lower = q.lower()
    
    # Search in topic names and languages
    for topic in topics:
        topic_name = topic["topicName"].lower()
        language = topic["language"].lower()
        
        if query_lower in topic_name or query_lower in language:
            suggestions.append({
                "suggestion": topic["topicName"],
                "type": "topic",
                "language": topic["language"],
                "topicId": topic["id"]
            })
    
    # Add some generic programming concept suggestions
    programming_concepts = [
        "loops", "functions", "variables", "arrays", "objects", "classes",
        "inheritance", "polymorphism", "recursion", "algorithms", "data structures"
    ]
    
    for concept in programming_concepts:
        if query_lower in concept.lower() and len(suggestions) < limit:
            suggestions.append({
                "suggestion": concept.title(),
                "type": "concept",
                "language": "General"
            })
    
    return SuccessResponse(
        success=True,
        message="Search suggestions retrieved",
        data={"suggestions": suggestions[:limit]}
    )

@router.get("/global", response_model=SuccessResponse)
async def search_content(
    q: str = Query(..., description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category: topics, videos, concepts"),
    language: Optional[str] = Query(None, description="Filter by programming language"),
    limit: int = Query(20, ge=1, le=50, description="Maximum number of results")
):
    """Global search across all content"""
    query_lower = q.lower()
    results = []
    
    # Search topics
    if not category or category == "topics":
        topics = get_all_topics()
        for topic in topics:
            if language and topic["language"].lower() != language.lower():
                continue
                
            # Check if query matches topic name, language, or overview
            topic_text = f"{topic['topicName']} {topic['language']} {topic['overview']}".lower()
            if query_lower in topic_text:
                results.append({
                    "type": "topic",
                    "id": topic["id"],
                    "title": topic["topicName"],
                    "language": topic["language"],
                    "difficulty": topic["difficulty"],
                    "overview": topic["overview"][:200] + "..." if len(topic["overview"]) > 200 else topic["overview"],
                    "relevanceScore": 100 if query_lower in topic["topicName"].lower() else 70
                })
    
    # Mock video search results
    if not category or category == "videos":
        mock_videos = [
            {
                "type": "video",
                "id": "vid-search-1",
                "title": f"Introduction to {q.title()}",
                "language": language or "Python",
                "duration": "15:30",
                "youtubeId": "dQw4w9WgXcQ",
                "relevanceScore": 85
            },
            {
                "type": "video", 
                "id": "vid-search-2",
                "title": f"Advanced {q.title()} Techniques",
                "language": language or "Java",
                "duration": "22:15",
                "youtubeId": "dQw4w9WgXcQ",
                "relevanceScore": 75
            }
        ]
        
        for video in mock_videos:
            if query_lower in video["title"].lower():
                results.append(video)
    
    # Sort by relevance score
    results.sort(key=lambda x: x.get("relevanceScore", 0), reverse=True)
    
    return SuccessResponse(
        success=True,
        message=f"Search results for '{q}'",
        data={
            "query": q,
            "totalResults": len(results),
            "results": results[:limit],
            "filters": {
                "category": category,
                "language": language
            }
        }
    )

@router.delete("/recent", response_model=SuccessResponse)
async def clear_search_history(current_user: dict = Depends(get_current_user_from_token)):
    """Clear user's search history"""
    # In production, this would clear the user's search history from database
    from app.data import MOCK_SEARCH_HISTORY
    user_id = current_user["id"]
    if user_id in MOCK_SEARCH_HISTORY:
        MOCK_SEARCH_HISTORY[user_id] = []
    
    return SuccessResponse(
        success=True,
        message="Search history cleared successfully"
    )

@router.get("/trending", response_model=SuccessResponse)
async def get_trending_searches():
    """Get trending/popular search queries"""
    trending = [
        {"query": "Python loops", "count": 145, "trend": "up"},
        {"query": "Java inheritance", "count": 132, "trend": "up"},
        {"query": "SQL joins", "count": 98, "trend": "stable"},
        {"query": "React hooks", "count": 87, "trend": "down"},
        {"query": "Algorithm complexity", "count": 76, "trend": "up"}
    ]
    
    return SuccessResponse(
        success=True,
        message="Trending searches retrieved successfully",
        data={"trending": trending}
    )