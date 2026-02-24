from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any
from app.models import User, UserUpdate, UserStats, SuccessResponse
from app.data import get_user_by_id, MOCK_USERS
from app.core.auth import get_current_user_from_token

router = APIRouter()

@router.get("/profile", response_model=SuccessResponse)
async def get_user_profile(current_user: dict = Depends(get_current_user_from_token)):
    """Get current user profile"""
    # Remove password from response
    user_data = {k: v for k, v in current_user.items() if k != "password"}
    
    return SuccessResponse(
        success=True,
        message="Profile retrieved successfully",
        data={"user": user_data}
    )

@router.put("/profile", response_model=SuccessResponse)
async def update_user_profile(
    updates: UserUpdate,
    current_user: dict = Depends(get_current_user_from_token)
):
    """Update user profile"""
    user = get_user_by_id(current_user["id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    
    # Update user data
    if updates.name is not None:
        user["name"] = updates.name
    if updates.preferred_style is not None:
        user["preferredStyle"] = updates.preferred_style
    
    # Remove password from response
    user_data = {k: v for k, v in user.items() if k != "password"}
    
    return SuccessResponse(
        success=True,
        message="Profile updated successfully",
        data={"user": user_data}
    )

@router.get("/stats", response_model=SuccessResponse)
async def get_user_stats(current_user: dict = Depends(get_current_user_from_token)):
    """Get user statistics for profile page"""
    user = current_user
    
    # Calculate stats
    stats = {
        "topicsCompleted": len(user["completedTopics"]),
        "totalTopics": len(user["completedTopics"]) + len(user["pendingTopics"]) + len(user["inProgressTopics"]),
        "quizzesTaken": len(user["completedTopics"]),
        "avgScore": 72,  # Mock average
        "streak": 12,
        "totalHours": 34,
        "joinDate": "Jan 2026",
        "rank": user.get("rank", 3),
        "badges": [
            {"name": "First Quiz", "icon": "🏅", "earned": True},
            {"name": "Week Streak", "icon": "🔥", "earned": True},
            {"name": "Perfect Score", "icon": "⭐", "earned": True},
            {"name": "Night Owl", "icon": "🦉", "earned": True},
            {"name": "Speed Demon", "icon": "⚡", "earned": False},
            {"name": "Completionist", "icon": "🏆", "earned": False},
        ],
        "languages": [
            {"name": "Python", "level": 78, "color": "bg-blue-500"},
            {"name": "Java", "level": 55, "color": "bg-orange-500"},
            {"name": "C", "level": 65, "color": "bg-gray-600"},
            {"name": "SQL", "level": 70, "color": "bg-emerald-500"},
        ]
    }
    
    return SuccessResponse(
        success=True,
        message="User stats retrieved successfully",
        data={"stats": stats}
    )

@router.get("/{user_id}/analytics", response_model=SuccessResponse) 
async def get_user_analytics(user_id: str):
    """Get analytics data for a specific user"""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    
    analytics = {
        "progressOverTime": [
            {"date": "2026-02-01", "score": 20},
            {"date": "2026-02-10", "score": 45},
            {"date": "2026-02-20", "score": 85},
        ],
        "topicPerformance": [
            {"topic": "Python Loops", "score": 85, "difficulty": "Beginner"},
            {"topic": "Java OOP", "score": 70, "difficulty": "Intermediate"},
        ],
        "studyPattern": {
            "mostActiveHour": "20:00",
            "averageSessionLength": "45 minutes",
            "streakData": {"current": 12, "longest": 18}
        }
    }
    
    return SuccessResponse(
        success=True,
        message="Analytics retrieved successfully",
        data={"analytics": analytics}
    )