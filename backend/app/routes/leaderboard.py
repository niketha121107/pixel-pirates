from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Dict, Any, Optional
from app.models import LeaderboardEntry, SuccessResponse
from app.data import get_leaderboard, get_user_by_id
from app.core.auth import get_current_user_from_token
import math

router = APIRouter()

@router.get("", response_model=SuccessResponse)
async def get_global_leaderboard(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user_from_token)
):
    """Get global leaderboard with pagination"""
    leaderboard_data = get_leaderboard()
    
    # Calculate pagination
    total_entries = len(leaderboard_data)
    total_pages = math.ceil(total_entries / limit)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    
    paginated_data = leaderboard_data[start_idx:end_idx]
    
    # Find current user's position
    current_user_entry = None
    for entry in leaderboard_data:
        if entry["userId"] == current_user["id"]:
            current_user_entry = entry
            break
    
    return SuccessResponse(
        success=True,
        message="Leaderboard retrieved successfully",
        data={
            "leaderboard": paginated_data,
            "pagination": {
                "currentPage": page,
                "totalPages": total_pages,
                "totalEntries": total_entries,
                "hasNext": page < total_pages,
                "hasPrevious": page > 1
            },
            "currentUser": current_user_entry
        }
    )

@router.get("/top/{count}", response_model=SuccessResponse)
async def get_top_users(count: int = 10):
    """Get top N users from leaderboard"""
    if count > 100:
        count = 100
    
    leaderboard_data = get_leaderboard()
    top_users = leaderboard_data[:count]
    
    return SuccessResponse(
        success=True,
        message=f"Top {count} users retrieved successfully",
        data={"topUsers": top_users}
    )

@router.get("/user-rank", response_model=SuccessResponse)
async def get_user_rank(current_user: dict = Depends(get_current_user_from_token)):
    """Get current user's rank and nearby users"""
    leaderboard_data = get_leaderboard()
    user = current_user
    user_id = user["id"]
    
    # Find user's position in leaderboard
    user_rank = None
    user_entry = None
    
    for i, entry in enumerate(leaderboard_data):
        if entry["userId"] == user_id:
            user_rank = i + 1
            user_entry = entry
            break
    
    if user_rank is None:
        # User not in leaderboard yet, create mock entry
        user_entry = {
            "rank": len(leaderboard_data) + 1,
            "userId": user_id,
            "name": user["name"],
            "score": user.get("totalScore", 0),
            "topicsCompleted": len(user.get("completedTopics", [])),
            "avatar": f"https://api.dicebear.com/7.x/avataaars/svg?seed={user['name']}"
        }
        user_rank = user_entry["rank"]
    
    # Get nearby users (2 above and below)
    nearby_users = []
    start = max(0, user_rank - 3)
    end = min(len(leaderboard_data), user_rank + 2)
    
    for i in range(start, end):
        if i < len(leaderboard_data):
            nearby_users.append(leaderboard_data[i])
    
    # If user not in main leaderboard, add their entry
    if user_rank > len(leaderboard_data):
        nearby_users.append(user_entry)
    
    return SuccessResponse(
        success=True,
        message="User rank retrieved successfully",
        data={
            "userRank": user_rank,
            "userEntry": user_entry,
            "nearbyUsers": nearby_users,
            "totalUsers": len(leaderboard_data) + (1 if user_rank > len(leaderboard_data) else 0)
        }
    )

@router.get("/language/{language}", response_model=SuccessResponse)
async def get_language_leaderboard(language: str):
    """Get leaderboard filtered by programming language"""
    # This is a mock implementation - in production, you'd filter by actual language performance
    leaderboard_data = get_leaderboard()
    
    # Mock filtering by adding language-specific scores
    language_leaderboard = []
    for entry in leaderboard_data:
        # Mock language-specific performance
        language_score = entry["score"] * 0.8 if language.lower() == "python" else entry["score"] * 0.6
        
        language_entry = entry.copy()
        language_entry["languageScore"] = int(language_score)
        language_entry["language"] = language
        language_leaderboard.append(language_entry)
    
    # Sort by language-specific score
    language_leaderboard.sort(key=lambda x: x["languageScore"], reverse=True)
    
    # Update ranks
    for i, entry in enumerate(language_leaderboard):
        entry["rank"] = i + 1
    
    return SuccessResponse(
        success=True,
        message=f"{language} leaderboard retrieved successfully",
        data={"leaderboard": language_leaderboard[:50]}  # Top 50
    )