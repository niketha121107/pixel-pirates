from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Dict, Any, Optional
from app.models import SuccessResponse
from app.data import get_user_by_id, get_all_topics
from app.core.auth import get_current_user_from_token
from datetime import datetime, timedelta
import random

router = APIRouter()

@router.get("/dashboard", response_model=SuccessResponse)
async def get_dashboard_analytics(current_user: dict = Depends(get_current_user_from_token)):
    """Get analytics data for dashboard"""
    user = current_user
    
    topics = get_all_topics()
    completed = len(user.get("completedTopics", []))
    in_progress = len(user.get("inProgressTopics", []))
    pending = len(user.get("pendingTopics", []))
    total_topics = completed + in_progress + pending
    
    analytics = {
        "overview": {
            "totalTopics": total_topics,
            "completedTopics": completed,
            "inProgressTopics": in_progress,
            "pendingTopics": pending,
            "completionRate": (completed / total_topics * 100) if total_topics > 0 else 0,
            "averageScore": 75.5,
            "currentStreak": 12,
            "totalStudyTime": 34  # hours
        },
        "recentActivity": [
            {"date": "2026-02-24", "action": "Completed Python Loops quiz", "score": 85},
            {"date": "2026-02-23", "action": "Watched Java OOP video", "duration": "18:30"},
            {"date": "2026-02-22", "action": "Started SQL Fundamentals topic", "progress": "in-progress"},
        ],
        "topicsProgress": [
            {"topicId": "topic-1", "name": "Python Loops", "progress": 100, "score": 85},
            {"topicId": "topic-2", "name": "Java OOP Basics", "progress": 60, "score": 0},
        ]
    }
    
    return SuccessResponse(
        success=True,
        message="Dashboard analytics retrieved successfully",
        data={"analytics": analytics}
    )

@router.get("/progress", response_model=SuccessResponse)
async def get_progress_analytics(
    period: str = Query("30d", description="Time period: 7d, 30d, 90d, 1y"),
    current_user: dict = Depends(get_current_user_from_token)
):
    """Get detailed progress analytics over time"""
    user = current_user
    
    # Generate mock progress data based on period
    days = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}.get(period, 30)
    base_date = datetime.now() - timedelta(days=days)
    
    progress_data = []
    cumulative_score = 0
    
    for i in range(days):
        date = base_date + timedelta(days=i)
        # Mock daily progress
        daily_gain = random.randint(0, 5) if random.random() > 0.7 else 0
        cumulative_score += daily_gain
        
        progress_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "cumulativeScore": cumulative_score,
            "dailyGain": daily_gain,
            "topicsCompleted": cumulative_score // 20,  # Mock topics completed
            "studyTime": random.randint(0, 180) if daily_gain > 0 else 0  # minutes
        })
    
    analytics = {
        "period": period,
        "progressData": progress_data,
        "summary": {
            "totalGain": cumulative_score,
            "averageDailyGain": cumulative_score / days,
            "activeDays": len([d for d in progress_data if d["dailyGain"] > 0]),
            "totalStudyTime": sum(d["studyTime"] for d in progress_data)
        }
    }
    
    return SuccessResponse(
        success=True,
        message="Progress analytics retrieved successfully",
        data={"analytics": analytics}
    )

@router.get("/performance", response_model=SuccessResponse)
async def get_performance_analytics(current_user: dict = Depends(get_current_user_from_token)):
    """Get performance analytics by topic and language"""
    user = current_user
    
    # Mock performance data
    performance = {
        "byLanguage": [
            {"language": "Python", "averageScore": 85, "topicsCompleted": 3, "timeSpent": 45},
            {"language": "Java", "averageScore": 72, "topicsCompleted": 2, "timeSpent": 38},
            {"language": "C", "averageScore": 68, "topicsCompleted": 1, "timeSpent": 25},
            {"language": "SQL", "averageScore": 90, "topicsCompleted": 1, "timeSpent": 20},
        ],
        "byDifficulty": [
            {"difficulty": "Beginner", "averageScore": 88, "topicsCompleted": 4, "successRate": 95},
            {"difficulty": "Intermediate", "averageScore": 75, "topicsCompleted": 2, "successRate": 80},
            {"difficulty": "Advanced", "averageScore": 65, "topicsCompleted": 1, "successRate": 70},
        ],
        "weakAreas": [
            {"area": "Advanced Algorithms", "score": 45, "needsImprovement": True},
            {"area": "System Design", "score": 55, "needsImprovement": True},
        ],
        "strongAreas": [
            {"area": "Basic Syntax", "score": 95, "strength": True},
            {"area": "Data Structures", "score": 88, "strength": True},
        ]
    }
    
    return SuccessResponse(
        success=True,
        message="Performance analytics retrieved successfully",
        data={"performance": performance}
    )

@router.get("/streaks", response_model=SuccessResponse)
async def get_streak_analytics(current_user: dict = Depends(get_current_user_from_token)):
    """Get streak and consistency analytics"""
    user = current_user
    
    # Generate mock streak data
    current_date = datetime.now()
    streak_data = []
    
    for i in range(30):  # Last 30 days
        date = current_date - timedelta(days=i)
        has_activity = random.random() > 0.3  # 70% chance of activity
        
        streak_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "hasActivity": has_activity,
            "studyTime": random.randint(15, 120) if has_activity else 0,
            "topicsStudied": random.randint(1, 3) if has_activity else 0
        })
    
    streak_data.reverse()  # Oldest to newest
    
    # Calculate current streak
    current_streak = 0
    for day in reversed(streak_data):
        if day["hasActivity"]:
            current_streak += 1
        else:
            break
    
    analytics = {
        "currentStreak": current_streak,
        "longestStreak": 18,  # Mock longest streak
        "streakData": streak_data,
        "consistency": {
            "activeDays": len([d for d in streak_data if d["hasActivity"]]),
            "totalDays": len(streak_data),
            "consistencyRate": len([d for d in streak_data if d["hasActivity"]]) / len(streak_data) * 100
        }
    }
    
    return SuccessResponse(
        success=True,
        message="Streak analytics retrieved successfully", 
        data={"streaks": analytics}
    )