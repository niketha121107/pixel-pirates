"""
Adaptive Learning Routes — Uses Gemini 2.5 Flash to analyze user performance
and dynamically adjust explanations, quizzes, and recommendations.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional
from app.models import SuccessResponse
from app.data import (
    get_user_by_id,
    get_topic_by_id,
    get_topic_progress,
    get_user_feedback,
    get_mock_results,
)
from app.services.adaptive_engine_service import adaptive_engine_service
from app.core.auth import get_current_user_from_token
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/analyze/{topic_id}", response_model=SuccessResponse)
async def analyze_user_for_topic(
    topic_id: str,
    current_user: dict = Depends(get_current_user_from_token),
):
    """Analyze user performance on a topic and return adaptive recommendations using Gemini."""
    topic = get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    user_id = current_user["id"]
    progress = get_topic_progress(user_id, topic_id)
    feedback = get_user_feedback(user_id, topic_id)
    quiz_scores = current_user.get("quizScores", {})
    mock_results = get_mock_results(user_id)

    # Build user data for Gemini analysis
    user_data = {
        "name": current_user["name"],
        "topicName": topic["topicName"],
        "difficulty": topic["difficulty"],
        "language": topic["language"],
        "quizScore": quiz_scores.get(topic_id),
        "completedTopics": len(current_user.get("completedTopics", [])),
        "totalTopics": len(current_user.get("completedTopics", [])) + len(current_user.get("pendingTopics", [])) + len(current_user.get("inProgressTopics", [])),
        "topicProgress": progress,
        "feedback": feedback,
        "recentMockResults": mock_results[:5],
        "preferredStyle": current_user.get("preferredStyle", "visual"),
    }

    try:
        analysis = await adaptive_engine_service.analyze_learning_progress(user_data)
    except Exception as e:
        logger.error(f"Adaptive analysis error: {e}")
        analysis = {
            "strengths": [],
            "weaknesses": [],
            "recommendations": ["Keep practicing this topic."],
            "nextTopics": [],
            "studyPlan": "Continue studying at your own pace.",
        }

    return SuccessResponse(
        success=True,
        message="Adaptive analysis complete",
        data={"analysis": analysis, "topicId": topic_id},
    )


@router.get("/explanation/{topic_id}", response_model=SuccessResponse)
async def get_adaptive_explanation(
    topic_id: str,
    current_user: dict = Depends(get_current_user_from_token),
):
    """Generate a personalized explanation adapted to the user's performance level using Gemini 2.5 Flash."""
    topic = get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    user_id = current_user["id"]
    progress = get_topic_progress(user_id, topic_id)
    quiz_scores = current_user.get("quizScores", {})
    score = quiz_scores.get(topic_id)

    # Determine user's level from performance data
    time_spent = 0
    attempts = 0
    for p in progress:
        time_spent += p.get("time_spent", 0)
        attempts += p.get("attempts", 0)

    if score is not None and score >= 80:
        level_hint = "advanced — user scored well, give deeper/challenging content"
    elif score is not None and score >= 50:
        level_hint = "intermediate — user understands basics but needs reinforcement"
    elif score is not None:
        level_hint = "beginner — user struggled, simplify heavily with lots of examples"
    elif time_spent > 600:
        level_hint = "struggling — user spent a long time, provide very simple step-by-step"
    else:
        level_hint = "new — first exposure, start with fundamentals"

    style = current_user.get("preferredStyle", "visual")
    additional = (
        f"User level assessment: {level_hint}. "
        f"Time spent so far: {time_spent}s. Attempts: {attempts}. "
        f"Previous score: {score}."
    )

    try:
        explanation = await adaptive_engine_service.get_personalized_explanation(
            topic=topic["topicName"],
            user_preferred_style=style,
            difficulty_level=topic["difficulty"],
            additional_context=additional,
        )
    except Exception:
        explanation = topic.get("overview", "Explanation unavailable.")

    return SuccessResponse(
        success=True,
        message="Adaptive explanation generated",
        data={
            "topicId": topic_id,
            "topicName": topic["topicName"],
            "style": style,
            "levelHint": level_hint,
            "explanation": explanation,
        },
    )


@router.get("/quiz/{topic_id}", response_model=SuccessResponse)
async def get_adaptive_quiz(
    topic_id: str,
    current_user: dict = Depends(get_current_user_from_token),
):
    """Generate an adaptive 10-question quiz adjusted to user performance using Gemini 2.5 Flash."""
    topic = get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    user_id = current_user["id"]
    progress = get_topic_progress(user_id, topic_id)
    quiz_scores = current_user.get("quizScores", {})
    mock_results = get_mock_results(user_id)

    # Build performance history for Gemini
    perf_history = []
    for p in progress:
        perf_history.append({
            "topic": topic["topicName"],
            "score": p.get("quiz_score", 0),
            "attempts": p.get("attempts", 1),
            "time_spent": p.get("time_spent", 0),
        })
    for mr in mock_results[:3]:
        perf_history.append({
            "topic": ", ".join(mr.get("topics", [])),
            "score": mr.get("percentage", 0),
            "attempts": 1,
        })

    try:
        questions = await adaptive_engine_service.generate_adaptive_quiz(
            topic_name=topic["topicName"],
            difficulty=topic["difficulty"],
            question_count=10,
            user_performance_history=perf_history,
        )
        if not questions:
            questions = topic.get("quiz", [])[:10]
            is_adaptive = False
        else:
            is_adaptive = True
    except Exception:
        questions = topic.get("quiz", [])[:10]
        is_adaptive = False

    return SuccessResponse(
        success=True,
        message="Adaptive quiz generated",
        data={
            "topicId": topic_id,
            "topicName": topic["topicName"],
            "questions": questions,
            "isAdaptive": is_adaptive,
            "totalQuestions": len(questions),
        },
    )
