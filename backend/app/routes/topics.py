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
    topics_with_progress = []
    for topic in topics:
        topic_data = topic.copy()
        
        # Determine status for this user
        if topic["id"] in user["completedTopics"]:
            topic_data["status"] = "completed"
            # Mock score for completed topics
            topic_data["score"] = 85  # You could store actual scores
            topic_data["total"] = 100
        elif topic["id"] in user["inProgressTopics"]:
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
    """Get detailed information about a specific topic"""
    topic = get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Topic not found"
        )
    
    user = current_user
    
    # Add user's progress status
    topic_data = topic.copy()
    if topic_id in user["completedTopics"]:
        topic_data["status"] = "completed"
        topic_data["userScore"] = 85  # Mock score
    elif topic_id in user["inProgressTopics"]:
        topic_data["status"] = "in-progress"
        topic_data["userScore"] = 0
    else:
        topic_data["status"] = "pending"
        topic_data["userScore"] = 0
    
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
        from app.services.openrouter_service import openrouter_service
        
        # Generate personalized explanation using AI
        ai_explanation = await openrouter_service.get_personalized_explanation(
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
async def get_topic_quiz(topic_id: str):
    """Get quiz questions for a specific topic"""
    topic = get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    return SuccessResponse(
        success=True,
        message="Quiz questions retrieved successfully",
        data={
            "topicId": topic_id,
            "topicName": topic["topicName"],
            "quiz": topic["quiz"]
        }
    )