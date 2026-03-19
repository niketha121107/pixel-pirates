from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any
from app.models import User, UserUpdate, UserStats, SuccessResponse, MockTestViolationIn
from app.data import get_user_by_id, MOCK_USERS, get_mock_test_integrity_status, register_mock_test_violation
from app.core.auth import get_current_user_from_token

router = APIRouter()

@router.get("/profile", response_model=SuccessResponse)
async def get_user_profile(current_user: dict = Depends(get_current_user_from_token)):
    """Get current user profile"""
    # Remove password from response
    user_data = {k: v for k, v in current_user.items() if k != "password"}
    user_data.setdefault("antiCheatWarnings", 0)
    user_data.setdefault("suspendedUntil", None)
    
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
    update_fields = {
        "name": updates.name,
        "preferredStyle": updates.preferred_style,
        "bio": updates.bio,
        "location": updates.location,
        "university": updates.university,
        "year": updates.year,
        "username": updates.username,
    }
    for key, value in update_fields.items():
        if value is not None:
            user[key] = value
    
    # Persist to MongoDB
    from app.data import update_user_in_db
    update_user_in_db(current_user["id"], {k: v for k, v in update_fields.items() if v is not None})
    
    # Remove password from response
    user_data = {k: v for k, v in user.items() if k != "password"}
    
    return SuccessResponse(
        success=True,
        message="Profile updated successfully",
        data={"user": user_data}
    )


@router.get("/mock-test-integrity", response_model=SuccessResponse)
async def get_mock_test_integrity(current_user: dict = Depends(get_current_user_from_token)):
    """Get current user's mock test warning/suspension state."""
    status_data = get_mock_test_integrity_status(current_user["id"])
    return SuccessResponse(
        success=True,
        message="Mock test integrity status retrieved successfully",
        data=status_data,
    )


@router.post("/mock-test-integrity", response_model=SuccessResponse)
async def report_mock_test_violation(
    violation: MockTestViolationIn,
    current_user: dict = Depends(get_current_user_from_token),
):
    """Record a prohibited action during a mock test."""
    result = register_mock_test_violation(current_user["id"], violation.reason)
    return SuccessResponse(
        success=True,
        message=result["message"],
        data=result,
    )

@router.get("/stats", response_model=SuccessResponse)
async def get_user_stats(current_user: dict = Depends(get_current_user_from_token)):
    """Get user statistics for profile page"""
    user = current_user
    
    # Compute real stats from user data
    completed = user.get("completedTopics", [])
    pending = user.get("pendingTopics", [])
    in_progress = user.get("inProgressTopics", [])
    quiz_scores = user.get("quizScores", {})
    
    total_topics = len(completed) + len(pending) + len(in_progress)
    avg_score = round(sum(quiz_scores.values()) / len(quiz_scores), 1) if quiz_scores else 0
    
    stats = {
        "topicsCompleted": len(completed),
        "totalTopics": total_topics,
        "quizzesTaken": len(quiz_scores),
        "avgScore": avg_score,
        "streak": user.get("streak", 0),
        "totalHours": user.get("totalHours", 0),
        "joinDate": user.get("createdAt", "N/A"),
        "rank": user.get("rank", total_topics),
        "badges": user.get("badges", []),
        "languages": user.get("languages", []),
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