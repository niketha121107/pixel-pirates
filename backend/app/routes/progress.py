"""
User Progress Routes — Detailed per-topic progress with time tracking and mock test results.
Includes dashboard metrics, learning progress graphs, and understanding feedback.
"""

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.models import SuccessResponse
from app.data import (
    save_topic_progress,
    get_topic_progress,
    save_mock_result,
    get_mock_results,
    save_understanding_feedback,
    get_understanding_feedback,
    calculate_progress_metrics,
    get_learning_progress_graph,
    get_completed_topics_with_scores,
)
from app.core.auth import get_current_user_from_token

router = APIRouter()


class TopicProgressIn(BaseModel):
    topic_id: str
    time_spent: int = 0  # seconds
    quiz_score: Optional[int] = None
    quiz_total: Optional[int] = None
    attempts: int = 1
    status: str = "in-progress"


class MockResultIn(BaseModel):
    topics: list
    score: int
    total_questions: int
    percentage: float
    time_taken: int = 0  # seconds
    answers: Optional[list] = []


class UnderstandingFeedbackIn(BaseModel):
    topic_id: str
    confidence_level: int  # 0-100 confidence slider value
    notes: Optional[str] = None


@router.post("/topic", response_model=SuccessResponse)
async def upsert_topic_progress(
    prog: TopicProgressIn,
    current_user: dict = Depends(get_current_user_from_token),
):
    saved = save_topic_progress(current_user["id"], prog.topic_id, prog.dict(exclude={"topic_id"}))
    return SuccessResponse(success=True, message="Progress saved", data={"progress": saved})


@router.get("/topic", response_model=SuccessResponse)
async def list_topic_progress(
    topic_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user_from_token),
):
    records = get_topic_progress(current_user["id"], topic_id)
    return SuccessResponse(success=True, message="Progress retrieved", data={"progress": records})


@router.post("/mock-result", response_model=SuccessResponse)
async def save_mock_test_result(
    result: MockResultIn,
    current_user: dict = Depends(get_current_user_from_token),
):
    saved = save_mock_result(current_user["id"], result.dict())
    return SuccessResponse(success=True, message="Mock test result saved", data={"result": saved})


@router.get("/mock-results", response_model=SuccessResponse)
async def list_mock_test_results(
    current_user: dict = Depends(get_current_user_from_token),
):
    results = get_mock_results(current_user["id"])
    return SuccessResponse(success=True, message="Mock results retrieved", data={"results": results})


@router.post("/understanding-feedback", response_model=SuccessResponse)
async def save_understanding_feedback_endpoint(
    feedback: UnderstandingFeedbackIn,
    current_user: dict = Depends(get_current_user_from_token),
):
    """
    Save self-assessed confidence/understanding feedback for a topic.
    
    FEATURE: Understanding Feedback (Feature 5)
    Purpose: Integrate student self-assessment of comprehension via confidence slider
    
    Input:
    - topic_id: The topic being evaluated
    - confidence_level: 0-100% value from confidence slider (how well student understands)
    - notes: Optional additional comments
    
    Storage:
    - Each confidence value stored with topic_id and timestamp
    - Scoped to authenticated student (data isolation)
    - Updates are immediate
    
    Impact:
    - Values feed into Avg Understanding metric calculation
    - Avg Understanding = Average of all confidence values per student
    - Reflected in dashboard metrics on next refresh
    
    Returns:
    - Saved feedback record with timestamp
    """
    saved = save_understanding_feedback(current_user["id"], feedback.topic_id, feedback.dict())
    return SuccessResponse(success=True, message="Understanding feedback saved", data={"feedback": saved})


@router.get("/understanding-feedback", response_model=SuccessResponse)
async def get_understanding_feedback_endpoint(
    topic_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user_from_token),
):
    """
    Retrieve understanding feedback for one or all topics.
    
    FEATURE: Understanding Feedback (Feature 5)
    Purpose: Get all self-assessed confidence values for the student
    
    Parameters:
    - topic_id (optional): If provided, returns feedback for specific topic only
    - If omitted, returns all feedback records for student
    
    Data Structure:
    - topic_id: Topic identifier
    - confidence_level: 0-100% confidence value
    - saved_at: Timestamp of when feedback was saved
    
    Data Integrity:
    - Only returns feedback for authenticated student (user isolation)
    - Cannot access other students' feedback
    - Scoped by current user ID from JWT token
    
    Usage:
    - GET /progress/understanding-feedback (all topics)
    - GET /progress/understanding-feedback?topic_id=data_types (specific topic)
    """
    records = get_understanding_feedback(current_user["id"], topic_id)
    return SuccessResponse(success=True, message="Understanding feedback retrieved", data={"feedback": records})


@router.get("/dashboard-metrics", response_model=SuccessResponse)
async def get_dashboard_metrics(
    current_user: dict = Depends(get_current_user_from_token),
):
    """
    Get complete dashboard metrics for Student Progress Page in single call.
    
    COMPLETE FEATURE INTEGRATION - All 6 components:
    
    1. LEARNING PROGRESS GRAPH (7-day engagement tracking)
    2. METRICS UPDATES (Topics Done, Avg Score, Time Learned, Avg Understanding)
    3. PIE CHART COMPLETION (completion_percentage = Topics Done / Total × 100)
    4. COMPLETED TOPICS & SCORES (detailed records with dates & times)
    5. UNDERSTANDING FEEDBACK (confidence slider values)
    6. DATA INTEGRITY (all scoped to current user)
    
    Output Data:
    - metrics: Topics Done, Total Topics, Avg Score, Time Learned (seconds), 
              Avg Understanding,Completion %
    - learning_progress_graph: 7-day engagement data (day, date, engagement 0-1)
    - pie_chart: completed count, remaining count, completion percentage
    - completed_topics: [topic_name, date (DD/MM/YYYY), score, percentage, 
                         understanding_level, time_spent (HH:MM:SS), attempts]
    - understanding_feedback: has_feedback flag, list of all feedback records
    
    Score Mapping (for engagement graph):
    - 0% → 0, 1-25% → 0.25, 26-50% → 0.5, 51-75% → 0.75, 76-100% → 1
    
    Data Isolation:
    - All queries scoped to current_user ID from JWT token
    - Each student only sees their own data
    - No cross-student data access possible
    
    Performance:
    - Single efficient call returns all dashboard data
    - Replaces 5 separate endpoint calls
    - Optimized for progress page rendering
    """
    metrics = calculate_progress_metrics(current_user["id"])
    return SuccessResponse(success=True, message="Dashboard metrics retrieved", data=metrics)


@router.get("/learning-progress-graph", response_model=SuccessResponse)
async def get_learning_progress(
    current_user: dict = Depends(get_current_user_from_token),
):
    """
    Get learning progress graph data for Student Progress Page.
    
    FEATURE 1: Learning Progress Graph
    Purpose: Plot engagement levels against completion dates as line graph
    
    Score Mapping:
    - 0% → 0 (no engagement)
    - 1–25% → 0.25 (low engagement)
    - 26–50% → 0.5 (medium engagement)
    - 51–75% → 0.75 (high engagement)
    - 76–100% → 1 (full engagement)
    
    Data Collected:
    - Past 7 days of learning activity
    - Each quiz score mapped to engagement value
    - Daily engagement accumulated from all completed quizzes
    
    Output Format:
    - day: Day abbreviation (Fri-Thu)
    - date: ISO format date (YYYY-MM-DD)
    - engagement: Mapped engagement level (0-1.0)
    
    Data Integrity:
    - Scoped to current authenticated student
    - Cannot access other students' progress data
    """
    graph_data = get_learning_progress_graph(current_user["id"])
    return SuccessResponse(success=True, message="Learning progress graph retrieved", data=graph_data)


@router.get("/completed-topics-scores", response_model=SuccessResponse)
async def get_completed_topics(
    current_user: dict = Depends(get_current_user_from_token),
):
    """
    Get list of completed topics for Student Progress Page with comprehensive metrics.
    
    FEATURE 4: Completed Topics & Scores
    Purpose: Display each completed topic with detailed performance metrics
    
    Topic Completion Criteria:
    - Topics with status="completed" OR quiz_score ≥ 70% are included
    
    Data per Topic:
    - topic_name: Display name of the topic
    - date_completed: Date in DD/MM/YYYY format
    - score: Numerical quiz score (e.g., 30/40)
    - percentage: Score as percentage (e.g., 75.0%)
    - understanding_level: Self-assessed confidence from slider (0-100%)
    - time_spent: Time spent formatted as HH:MM:SS
    - time_spent_seconds: Raw seconds for calculations
    - attempts: Number of quiz attempts
    
    Special Rules:
    - Reattempts update score/date but don't increase Topics Done counter
    - Sorted by date (most recent first)
    - Prevents double-counting for retakes
    
    Output:
    - CSV-compatible list of completed topics with all metrics
    - Ready for export and dashboard display
    
    Data Integrity:
    - Scoped to authenticated student only
    - User isolation enforced via user_id
    - Cannot see other students' completed topics
    """
    topics = get_completed_topics_with_scores(current_user["id"])
    return SuccessResponse(success=True, message="Completed topics retrieved", data={"topics": topics})
