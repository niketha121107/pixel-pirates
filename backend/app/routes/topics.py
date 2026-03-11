from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Dict, Any, Optional
from app.models import Topic, TopicProgress, TopicStatus, SuccessResponse
from app.data import get_all_topics, get_topic_by_id, get_user_by_id, update_user_topic_progress
from app.core.auth import get_current_user_from_token

router = APIRouter()

@router.get("", response_model=SuccessResponse)
async def get_topics(
    language: Optional[str] = Query(None, description="Filter by programming language"),
    status: Optional[str] = Query(None, description="Filter by completion status"),
    search: Optional[str] = Query(None, description="Search topics by title"),
    current_user: dict = Depends(get_current_user_from_token)
):
    """Get all topics with user's progress status"""
    topics = get_all_topics()
    user = current_user
    
    # Add user progress to each topic
    quiz_scores = user.get("quizScores", {})
    topics_with_progress = []
    for topic in topics:
        topic_data = topic.copy()
        
        # Determine status for this user
        if topic["id"] in user.get("completedTopics", []):
            topic_data["status"] = "completed"
            topic_data["score"] = quiz_scores.get(topic["id"], 0)
            topic_data["total"] = 100
        elif topic["id"] in user.get("inProgressTopics", []):
            topic_data["status"] = "in-progress"
            topic_data["score"] = 0
            topic_data["total"] = 100
        else:
            topic_data["status"] = "pending"
            topic_data["score"] = 0
            topic_data["total"] = 100
        
        # Apply filters
        if language and topic["language"].lower() != language.lower():
            continue
        if status and topic_data["status"] != status:
            continue
        if search and search.lower() not in topic["topicName"].lower():
            continue
            
        topics_with_progress.append(topic_data)
    
    return SuccessResponse(
        success=True,
        message="Topics retrieved successfully",
        data={"topics": topics_with_progress}
    )

@router.get("/{topic_id}", response_model=SuccessResponse)
async def get_topic_details(
    topic_id: str,
    current_user: dict = Depends(get_current_user_from_token)
):
    """Get detailed information about a specific topic, with live YouTube videos."""
    topic = get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Topic not found"
        )
    
    user = current_user
    
    # Add user's progress status
    quiz_scores = user.get("quizScores", {})
    topic_data = topic.copy()
    if topic_id in user.get("completedTopics", []):
        topic_data["status"] = "completed"
        topic_data["userScore"] = quiz_scores.get(topic_id, 0)
    elif topic_id in user.get("inProgressTopics", []):
        topic_data["status"] = "in-progress"
        topic_data["userScore"] = 0
    else:
        topic_data["status"] = "pending"
        topic_data["userScore"] = 0

    # --- Dynamically fetch YouTube videos for the topic ---
    import asyncio, logging
    _log = logging.getLogger(__name__)
    try:
        from app.services.youtube_service import youtube_service
        live_videos = await asyncio.wait_for(
            youtube_service.search_for_topic(
                topic_name=topic["topicName"],
                language=topic.get("language", ""),
                max_results=5,
            ),
            timeout=8.0,
        )
        if live_videos:
            topic_data["recommendedVideos"] = live_videos
            _log.info(f"Fetched {len(live_videos)} live YouTube videos for {topic['topicName']}")
        else:
            _log.info(f"YouTube API returned no results — using stored videos for {topic['topicName']}")
    except asyncio.TimeoutError:
        _log.warning(f"YouTube API timed out for {topic['topicName']} — using stored videos")
    except Exception as e:
        _log.warning(f"YouTube API error for {topic['topicName']}: {e} — using stored videos")

    return SuccessResponse(
        success=True,
        message="Topic details retrieved successfully",
        data={"topic": topic_data}
    )

@router.put("/{topic_id}/status", response_model=SuccessResponse)
async def update_topic_status(
    topic_id: str,
    progress: TopicProgress,
    current_user: dict = Depends(get_current_user_from_token)
):
    """Update user's progress status for a topic"""
    topic = get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Topic not found"
        )
    
    success = update_user_topic_progress(
        current_user["id"], 
        topic_id, 
        progress.status.value,
        progress.score
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return SuccessResponse(
        success=True,
        message=f"Topic status updated to {progress.status}",
        data={
            "topicId": topic_id,
            "status": progress.status.value,
            "score": progress.score
        }
    )

@router.get("/{topic_id}/explanation", response_model=SuccessResponse)
async def get_personalized_explanation(
    topic_id: str,
    style: Optional[str] = Query(None, description="Explanation style: visual, simplified, logical, analogy"),
    current_user: dict = Depends(get_current_user_from_token)
):
    """Get AI-generated personalized explanation for a topic"""
    topic = get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Topic not found"
        )
    
    user = current_user
    
    # Use user's preferred style if not specified
    explanation_style = style or user.get("preferredStyle", "visual")
    
    try:
        from app.services.adaptive_engine_service import adaptive_engine_service
        
        # Generate personalized explanation using Gemini AI
        ai_explanation = await adaptive_engine_service.get_personalized_explanation(
            topic=topic["topicName"],
            user_preferred_style=explanation_style,
            difficulty_level=topic["difficulty"],
            additional_context=topic["overview"]
        )
        
        # Also include existing explanations
        existing_explanations = topic.get("explanations", [])
        
        return SuccessResponse(
            success=True,
            message="Personalized explanation generated",
            data={
                "topicId": topic_id,
                "topicName": topic["topicName"],
                "aiExplanation": {
                    "style": explanation_style,
                    "content": ai_explanation,
                    "generated": True
                },
                "existingExplanations": existing_explanations
            }
        )
        
    except Exception as e:
        # Fallback to existing explanations
        existing_explanations = topic.get("explanations", [])
        preferred_explanation = next(
            (exp for exp in existing_explanations if exp["style"] == explanation_style),
            existing_explanations[0] if existing_explanations else None
        )
        
        return SuccessResponse(
            success=True,
            message="Existing explanation retrieved",
            data={
                "topicId": topic_id,
                "topicName": topic["topicName"],
                "explanation": preferred_explanation,
                "existingExplanations": existing_explanations
            }
        )

@router.get("/{topic_id}/quiz", response_model=SuccessResponse)
async def get_topic_quiz(
    topic_id: str,
    subtopicId: Optional[str] = Query(None, description="Optional subtopic ID to get subtopic-specific quiz"),
):
    """Get quiz questions for a specific topic or subtopic"""
    topic = get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    quiz = topic["quiz"]
    quiz_name = topic["topicName"]

    if subtopicId:
        for sub in topic.get("subtopics", []):
            if sub.get("id") == subtopicId:
                quiz = sub.get("quiz", topic["quiz"])
                quiz_name = sub.get("name", topic["topicName"])
                break

    return SuccessResponse(
        success=True,
        message="Quiz questions retrieved successfully",
        data={
            "topicId": topic_id,
            "topicName": quiz_name,
            "quiz": quiz
        }
    )