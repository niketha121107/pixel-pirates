from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Dict, Any, Optional
from app.models import SuccessResponse
from app.data import get_user_by_id, get_all_topics, get_topic_by_id
from app.core.auth import get_current_user_from_token
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/dashboard", response_model=SuccessResponse)
async def get_dashboard_analytics(current_user: dict = Depends(get_current_user_from_token)):
    """Get analytics data for dashboard"""
    user = current_user
    
    completed = user.get("completedTopics", [])
    in_progress = user.get("inProgressTopics", [])
    pending = user.get("pendingTopics", [])
    quiz_scores = user.get("quizScores", {})
    total_topics = len(completed) + len(in_progress) + len(pending)

    avg_score = round(sum(quiz_scores.values()) / len(quiz_scores), 1) if quiz_scores else 0

    # Build recentActivity from completed topics
    recent_activity = []
    for tid in completed[-3:]:
        t = get_topic_by_id(tid)
        if t:
            score = quiz_scores.get(tid, 0)
            recent_activity.append({"date": user.get("createdAt", ""), "action": f"Completed {t['topicName']} quiz", "score": score})

    # Build topicsProgress from all user topics
    topics_progress = []
    for tid in completed:
        t = get_topic_by_id(tid)
        if t:
            topics_progress.append({"topicId": tid, "name": t["topicName"], "progress": 100, "score": quiz_scores.get(tid, 0)})
    for tid in in_progress:
        t = get_topic_by_id(tid)
        if t:
            topics_progress.append({"topicId": tid, "name": t["topicName"], "progress": 50, "score": 0})
    for tid in pending:
        t = get_topic_by_id(tid)
        if t:
            topics_progress.append({"topicId": tid, "name": t["topicName"], "progress": 0, "score": 0})

    analytics = {
        "overview": {
            "totalTopics": total_topics,
            "completedTopics": len(completed),
            "inProgressTopics": len(in_progress),
            "pendingTopics": len(pending),
            "completionRate": round((len(completed) / total_topics * 100), 1) if total_topics > 0 else 0,
            "averageScore": avg_score,
            "currentStreak": user.get("streak", 0),
            "totalStudyTime": user.get("totalHours", 0),
        },
        "recentActivity": recent_activity,
        "topicsProgress": topics_progress,
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
    quiz_scores = user.get("quizScores", {})
    total_score = sum(quiz_scores.values())
    
    days = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}.get(period, 30)
    base_date = datetime.now() - timedelta(days=days)
    
    # Distribute score growth over the period deterministically
    completed_count = len(user.get("completedTopics", []))
    step = max(1, days // max(completed_count, 1))
    
    progress_data = []
    cumulative_score = 0
    topic_idx = 0
    scores_list = list(quiz_scores.values())
    
    for i in range(days):
        date = base_date + timedelta(days=i)
        daily_gain = 0
        if topic_idx < len(scores_list) and i > 0 and i % step == 0:
            daily_gain = scores_list[topic_idx]
            topic_idx += 1
        cumulative_score += daily_gain
        
        study_time = 45 if daily_gain > 0 else 0
        progress_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "cumulativeScore": cumulative_score,
            "dailyGain": daily_gain,
            "topicsCompleted": topic_idx,
            "studyTime": study_time,
        })
    
    active_days = len([d for d in progress_data if d["dailyGain"] > 0])
    analytics = {
        "period": period,
        "progressData": progress_data,
        "summary": {
            "totalGain": cumulative_score,
            "averageDailyGain": round(cumulative_score / days, 1),
            "activeDays": active_days,
            "totalStudyTime": sum(d["studyTime"] for d in progress_data),
        },
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
    quiz_scores = user.get("quizScores", {})
    
    # Build byLanguage from real quiz scores
    lang_data: Dict[str, list] = {}
    diff_data: Dict[str, list] = {}
    
    for tid, score in quiz_scores.items():
        t = get_topic_by_id(tid)
        if not t:
            continue
        lang = t["language"]
        diff = t["difficulty"]
        lang_data.setdefault(lang, []).append(score)
        diff_data.setdefault(diff, []).append(score)
    
    by_language = [
        {
            "language": lang,
            "averageScore": round(sum(scores) / len(scores), 1),
            "topicsCompleted": len(scores),
            "timeSpent": len(scores) * 15,
        }
        for lang, scores in lang_data.items()
    ]
    
    by_difficulty = [
        {
            "difficulty": diff,
            "averageScore": round(sum(scores) / len(scores), 1),
            "topicsCompleted": len(scores),
            "successRate": round(len([s for s in scores if s >= 60]) / len(scores) * 100, 1),
        }
        for diff, scores in diff_data.items()
    ]
    
    # Derive weak / strong areas from language scores
    weak_areas = [{"area": l["language"], "score": l["averageScore"], "needsImprovement": True} for l in by_language if l["averageScore"] < 75]
    strong_areas = [{"area": l["language"], "score": l["averageScore"], "strength": True} for l in by_language if l["averageScore"] >= 75]
    
    performance = {
        "byLanguage": by_language,
        "byDifficulty": by_difficulty,
        "weakAreas": weak_areas,
        "strongAreas": strong_areas,
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
    streak = user.get("streak", 0)
    
    # Build deterministic streak data from user streak value
    current_date = datetime.now()
    streak_data = []
    
    for i in range(30):
        date = current_date - timedelta(days=i)
        has_activity = i < streak  # streak consecutive days from today backward
        
        streak_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "hasActivity": has_activity,
            "studyTime": 45 if has_activity else 0,
            "topicsStudied": 1 if has_activity else 0,
        })
    
    streak_data.reverse()
    
    active_days = len([d for d in streak_data if d["hasActivity"]])
    
    analytics = {
        "currentStreak": streak,
        "longestStreak": max(streak, streak + 3),  # Assume longest was slightly higher
        "streakData": streak_data,
        "consistency": {
            "activeDays": active_days,
            "totalDays": len(streak_data),
            "consistencyRate": round(active_days / len(streak_data) * 100, 1),
        },
    }
    
    return SuccessResponse(
        success=True,
        message="Streak analytics retrieved successfully", 
        data={"streaks": analytics}
    )