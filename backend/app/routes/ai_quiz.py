#!/usr/bin/env python
"""
AI-Powered Quiz and Test Routes
All content generated on-demand using Gemini AI
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from app.core.auth import get_current_user_from_token
from app.models import SuccessResponse
from app.services.ai_content_service import ai_generator
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/quiz/{topic_id}", response_model=SuccessResponse)
async def get_ai_generated_quiz(
    topic_id: str,
    question_count: int = Query(5, ge=1, le=20),
    difficulty: str = Query("medium", regex="^(easy|medium|hard|mixed)$"),
    current_user: dict = Depends(get_current_user_from_token)
):
    """Get AI-generated quiz questions for a topic"""
    try:
        from app.data import get_topic_by_id
        topic = get_topic_by_id(topic_id)
        
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        topic_name = topic.get("topicName") or topic.get("name", "Programming Concept")
        
        logger.info(f"Generating {question_count} {difficulty} quiz questions for {topic_name}")
        
        # Generate fresh questions using AI
        questions = await ai_generator.generate_quiz_questions(
            topic_name=topic_name,
            num_questions=question_count,
            difficulty=difficulty
        )
        
        if not questions:
            raise HTTPException(
                status_code=500, 
                detail="Unable to generate quiz questions. Please try again."
            )
        
        return SuccessResponse(
            success=True,
            message=f"Generated {len(questions)} AI quiz questions",
            data={
                "topicId": topic_id,
                "topicName": topic_name,
                "questions": questions,
                "totalQuestions": len(questions),
                "difficulty": difficulty,
                "isAIGenerated": True
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-adaptive", response_model=SuccessResponse)
async def generate_adaptive_quiz(
    topic_id: str,
    question_count: int = Query(10, ge=5, le=20),
    current_user: dict = Depends(get_current_user_from_token)
):
    """Generate adaptive quiz based on user performance"""
    try:
        from app.data import get_topic_by_id
        topic = get_topic_by_id(topic_id)
        
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        topic_name = topic.get("topicName") or topic.get("name", "Programming Concept")
        difficulty = topic.get("difficulty", "medium")
        
        logger.info(f"Generating adaptive quiz for {topic_name}")
        
        # Generate with slight randomization for variety
        import random
        difficulty_options = ["easy", "medium", "hard"]
        weights = [0.3, 0.5, 0.2] if difficulty == "medium" else [0.2, 0.3, 0.5]
        selected_difficulty = random.choices(difficulty_options, weights=weights)[0]
        
        questions = await ai_generator.generate_quiz_questions(
            topic_name=topic_name,
            num_questions=question_count,
            difficulty=selected_difficulty
        )
        
        if not questions:
            raise HTTPException(status_code=500, detail="Failed to generate adaptive quiz")
        
        return SuccessResponse(
            success=True,
            message="Adaptive quiz generated",
            data={
                "topicId": topic_id,
                "topicName": topic_name,
                "questions": questions,
                "totalQuestions": len(questions),
                "isAdaptive": True
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating adaptive quiz: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/custom-topic", response_model=SuccessResponse)
async def generate_custom_topic_quiz(
    topic_name: str = Query(..., description="Any topic name for AI to generate questions about"),
    question_count: int = Query(5, ge=1, le=20, description="Number of questions to generate"),
    difficulty: str = Query("medium", regex="^(easy|medium|hard|mixed)$", description="Question difficulty level"),
    current_user: dict = Depends(get_current_user_from_token)
):
    """
    Generate AI quiz questions for ANY custom topic (not limited to database topics).
    Users can input any topic name and get instant AI-generated questions.
    """
    try:
        if not topic_name or topic_name.strip() == "":
            raise HTTPException(status_code=400, detail="Topic name cannot be empty")
        
        topic_name = topic_name.strip()
        logger.info(f"Generating AI quiz for custom topic: {topic_name} ({question_count} {difficulty} questions)")
        
        # Generate fresh questions using AI (no database lookup needed)
        questions = await ai_generator.generate_quiz_questions(
            topic_name=topic_name,
            num_questions=question_count,
            difficulty=difficulty
        )
        
        if not questions:
            raise HTTPException(
                status_code=500, 
                detail="Unable to generate quiz questions. Please try again or check your API key."
            )
        
        logger.info(f"✅ Successfully generated {len(questions)} AI questions for topic: {topic_name}")
        
        return SuccessResponse(
            success=True,
            message=f"Generated {len(questions)} AI quiz questions for '{topic_name}'",
            data={
                "topicName": topic_name,
                "questions": questions,
                "totalQuestions": len(questions),
                "difficulty": difficulty,
                "isAIGenerated": True,
                "isCustomTopic": True  # Flag to indicate this is custom topic
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating custom topic quiz: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")


@router.post("/mock-test", response_model=SuccessResponse)
async def generate_full_mock_test(
    topics: List[str] = Query(...),
    total_questions: int = Query(20, ge=10, le=100),
    difficulty_easy: int = Query(5, ge=0),
    difficulty_medium: int = Query(10, ge=0),
    difficulty_hard: int = Query(5, ge=0),
    current_user: dict = Depends(get_current_user_from_token)
):
    """Generate full mock test for multiple topics using AI"""
    try:
        if not topics:
            raise HTTPException(status_code=400, detail="At least one topic is required")
        
        # Validate topics exist
        from app.data import get_topic_by_id, get_all_topics
        all_topics = get_all_topics()
        valid_topics = []
        
        for topic_name in topics:
            # Find matching topic
            found = any(
                t.get("topicName", "").lower() == topic_name.lower() or 
                t.get("name", "").lower() == topic_name.lower()
                for t in all_topics
            )
            if found:
                valid_topics.append(topic_name)
        
        if not valid_topics:
            # If no exact matches, use all provided topics
            valid_topics = topics
        
        logger.info(f"Generating mock test with {total_questions} questions from topics: {valid_topics}")
        
        # Prepare difficulty mix
        difficulty_mix = {
            "easy": difficulty_easy,
            "medium": difficulty_medium,
            "hard": difficulty_hard
        }
        
        # Generate comprehensive mock test
        mock_test = await ai_generator.generate_mock_test(
            topics=valid_topics,
            total_questions=total_questions,
            difficulty_mix=difficulty_mix
        )
        
        if not mock_test.get("success"):
            raise HTTPException(status_code=500, detail="Failed to generate mock test")
        
        test_data = mock_test.get("data", {})
        questions = test_data.get("questions", [])
        
        return SuccessResponse(
            success=True,
            message=f"Generated comprehensive mock test with {len(questions)} questions",
            data={
                "metadata": test_data.get("metadata", {}),
                "questions": questions,
                "totalQuestions": len(questions),
                "isFullMockTest": True
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating mock test: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/evaluate", response_model=SuccessResponse)
async def evaluate_quiz_performance(
    topic_id: str,
    score: float = Query(..., ge=0, le=100),
    total_questions: int = Query(..., ge=1),
    current_user: dict = Depends(get_current_user_from_token)
):
    """Get AI-powered feedback on quiz performance"""
    try:
        from app.data import get_topic_by_id
        topic = get_topic_by_id(topic_id)
        
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        topic_name = topic.get("topicName") or topic.get("name", "Programming")
        
        # Generate intelligent recommendations
        recommendations = await ai_generator.generate_progress_recommendation(
            topic_name=topic_name,
            user_score=score,
            weak_areas=None
        )
        
        # Determine pass/fail
        passed = score >= 60
        
        return SuccessResponse(
            success=True,
            message="Performance evaluated",
            data={
                "passed": passed,
                "score": score,
                "recommendations": recommendations,
                "topicName": topic_name
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error evaluating performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-ai", response_model=SuccessResponse)
async def test_ai_generation(
    topic_name: str = Query("Python Functions"),
    question_count: int = Query(3, ge=1, le=10)
):
    """Test AI generation (no auth required for testing)"""
    try:
        logger.info(f"Testing AI generation for {topic_name}")
        
        questions = await ai_generator.generate_quiz_questions(
            topic_name=topic_name,
            num_questions=question_count,
            difficulty="mixed"
        )
        
        if questions:
            return SuccessResponse(
                success=True,
                message=f"AI generation working! Generated {len(questions)} questions",
                data={
                    "topic": topic_name,
                    "questionsGenerated": len(questions),
                    "sampleQuestion": questions[0] if questions else None
                }
            )
        else:
            raise HTTPException(status_code=500, detail="No questions generated")
    
    except Exception as e:
        logger.error(f"Error in AI test: {e}")
        raise HTTPException(status_code=500, detail=str(e))
