from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.models import QuizSubmission, QuizResult, SuccessResponse
from app.data import get_topic_by_id, get_user_by_id, update_user_topic_progress
from app.services.adaptive_engine_service import adaptive_engine_service
from app.core.auth import get_current_user_from_token

router = APIRouter()

class MockTestRequest(BaseModel):
    topics: List[str]
    difficulty_mix: Dict[str, int]  # {"Beginner": 5, "Intermediate": 3, "Advanced": 2}
    total_questions: int = 15


def _normalize_mock_type(raw_type: Any, index: int) -> str:
    raw = str(raw_type or '').strip().lower()
    if raw in {"mcq", "multiple_choice", "multiple-choice", "choose"}:
        return "mcq"
    if raw in {"fillup", "fill_up", "fillintheblank", "fill-in-the-blank", "blank"}:
        return "fillup"
    if raw in {"written", "qa", "q&a", "subjective", "essay"}:
        return "written"
    return ["mcq", "fillup", "written"][index % 3]

@router.post("/submit", response_model=SuccessResponse)
async def submit_quiz(
    submission: QuizSubmission,
    current_user: dict = Depends(get_current_user_from_token)
):
    """Submit quiz answers and get results with adaptive learning feedback"""
    topic = get_topic_by_id(submission.topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Topic not found"
        )
    
    # Grade the quiz
    quiz_questions = topic["quiz"]
    total_questions = len(quiz_questions)
    correct_count = 0
    correct_answers = []
    incorrect_answers = []
    weak_areas = []
    
    for answer in submission.answers:
        question = next((q for q in quiz_questions if q["id"] == answer.question_id), None)
        if question:
            if question["correctAnswer"] == answer.selected_answer:
                correct_count += 1
                correct_answers.append(answer.question_id)
            else:
                incorrect_answers.append(answer.question_id)
                # Track weak areas for adaptive learning
                weak_areas.append({
                    "questionId": answer.question_id,
                    "topic": topic["topicName"],
                    "concept": "General"  # In production, extract from question
                })
    
    # Calculate score and percentage
    score = correct_count
    percentage = (correct_count / total_questions) * 100 if total_questions > 0 else 0
    
    # Update user progress
    if percentage >= 70:  # Passing threshold
        update_user_topic_progress(current_user["id"], submission.topic_id, "completed", score)
    else:
        update_user_topic_progress(current_user["id"], submission.topic_id, "in-progress")
    
    # Generate evaluation feedback via adaptive engine (Gemini), fallback on failure.
    ai_weak_areas = []
    try:
        evaluation = await adaptive_engine_service.evaluate_quiz_attempt(
            topic_name=topic["topicName"],
            percentage=percentage,
            correct_count=correct_count,
            total_questions=total_questions,
            incorrect_question_ids=incorrect_answers,
            preferred_style=current_user.get("preferredStyle", "visual"),
        )
        feedback = evaluation.get("feedback") or "Great effort on the quiz! Keep practicing these concepts."
        ai_weak_areas = [
            {
                "questionId": "",
                "topic": topic["topicName"],
                "concept": wa.get("concept", "General"),
                "recommendation": wa.get("recommendation", "Practice more questions for this concept."),
            }
            for wa in evaluation.get("weakAreas", [])
            if isinstance(wa, dict)
        ]
    except Exception:
        feedback = "Great effort on the quiz! Keep practicing these concepts."
    
    result = QuizResult(
        topic_id=submission.topic_id,
        score=score,
        total_questions=total_questions,
        correct_answers=correct_answers,
        incorrect_answers=incorrect_answers,
        percentage=percentage,
        time_taken=submission.time_taken
    )
    
    return SuccessResponse(
        success=True,
        message="Quiz submitted successfully",
        data={
            "result": result.dict(),
            "passed": percentage >= 70,
            "feedback": feedback,
            "weakAreas": ai_weak_areas or weak_areas,
            "message": "Congratulations! You passed!" if percentage >= 70 else "Keep practicing and try again!"
        }
    )

@router.post("/adaptive", response_model=SuccessResponse)
async def generate_adaptive_quiz(
    topic_id: str,
    question_count: int = Query(10, ge=5, le=15, description="Number of questions"),
    current_user: dict = Depends(get_current_user_from_token)
):
    """Generate an adaptive quiz based on user's performance history"""
    topic = get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Topic not found"
        )
    
    user = current_user
    
    user = current_user
    
    try:
        # Mock performance history - in production, get from database
        performance_history = [
            {"topic": "Python Loops", "score": 60, "attempts": 2},
            {"topic": "Variables", "score": 85, "attempts": 1},
        ]
        
        # Generate adaptive quiz using adaptive engine (Gemini)
        adaptive_questions = await adaptive_engine_service.generate_adaptive_quiz(
            topic_name=topic["topicName"],
            difficulty=topic["difficulty"],
            user_performance_history=performance_history,
            question_count=question_count,
        )
        
        if not adaptive_questions:
            # Fallback to existing quiz questions
            adaptive_questions = topic["quiz"][:question_count]
        
        return SuccessResponse(
            success=True,
            message="Adaptive quiz generated successfully",
            data={
                "topicId": topic_id,
                "topicName": topic["topicName"],
                "questions": adaptive_questions,
                "isAdaptive": True,
                "totalQuestions": len(adaptive_questions)
            }
        )
        
    except Exception as e:
        # Fallback to regular quiz on error
        return SuccessResponse(
            success=True,
            message="Quiz generated (fallback mode)",
            data={
                "topicId": topic_id,
                "topicName": topic["topicName"],
                "questions": topic["quiz"][:question_count],
                "isAdaptive": False,
                "totalQuestions": len(topic["quiz"][:question_count])
            }
        )

@router.post("/mock-test", response_model=SuccessResponse)
async def generate_mock_test(
    test_request: MockTestRequest,
    current_user: dict = Depends(get_current_user_from_token)
):
    """Generate a comprehensive mock test using Gemini AI"""
    try:
        # Try to generate mock test using Gemini AI with a short timeout
        import asyncio
        try:
            mock_test = await asyncio.wait_for(
                adaptive_engine_service.generate_mock_test(
                    topics=test_request.topics,
                    difficulty_mix=test_request.difficulty_mix,
                    total_questions=test_request.total_questions
                ),
                timeout=10.0  # 10 second timeout for AI
            )
        except (asyncio.TimeoutError, Exception):
            mock_test = {"questions": None}
        
        if not mock_test.get("questions"):
            # Fallback to mixed questions from existing topics
            fallback_questions = []
            from app.data import get_all_topics
            all_topics = get_all_topics()

            for topic in all_topics:
                for q in topic.get("quiz", []):
                    fallback_questions.append({
                        **q,
                        "topic": topic.get("topicName", "Programming"),
                    })

            if not fallback_questions:
                fallback_questions = [{
                    "id": "fallback-1",
                    "type": "mcq",
                    "question": "Which keyword defines a function in Python?",
                    "options": ["func", "def", "function", "define"],
                    "correctAnswer": "def",
                    "correctIdx": 1,
                    "difficulty": "Beginner",
                    "topic": "Python",
                    "explanation": "Python functions are declared with the def keyword.",
                    "points": 10,
                }]

            expanded_questions = []
            idx = 0
            while len(expanded_questions) < test_request.total_questions:
                src = fallback_questions[idx % len(fallback_questions)]
                q_type = _normalize_mock_type(src.get("type"), idx)
                options = src.get("options") or []
                correct_idx = src.get("correctIdx")
                correct_answer = src.get("correctAnswer")
                if isinstance(correct_answer, int) and options:
                    try:
                        correct_answer = options[correct_answer]
                    except Exception:
                        correct_answer = ""

                expanded_questions.append({
                    "id": f"mq-{idx + 1}",
                    "type": q_type,
                    "question": src.get("question", ""),
                    "options": options,
                    "correctAnswer": str(correct_answer or ""),
                    "correctIdx": correct_idx if isinstance(correct_idx, int) else None,
                    "difficulty": src.get("difficulty", "Intermediate"),
                    "topic": src.get("topic", "Programming"),
                    "explanation": src.get("explanation", ""),
                    "points": src.get("points", 10 if q_type != "written" else 15),
                })
                idx += 1
            
            mock_test = {
                "metadata": {
                    "title": "Programming Mock Test",
                    "totalQuestions": test_request.total_questions,
                    "estimatedTime": "30 minutes",
                    "topics": test_request.topics
                },
                "questions": expanded_questions
            }

        # Normalize response shape and enforce requested length/types.
        normalized = []
        for i, q in enumerate(mock_test.get("questions", [])[: test_request.total_questions]):
            q_type = _normalize_mock_type(q.get("type"), i)
            options = q.get("options") or []
            correct_answer = q.get("correctAnswer")
            if isinstance(correct_answer, int) and options:
                try:
                    correct_answer = options[correct_answer]
                except Exception:
                    correct_answer = ""
            normalized.append({
                **q,
                "id": q.get("id", f"mq-{i + 1}"),
                "type": q_type,
                "correctAnswer": str(correct_answer or ""),
                "points": q.get("points", 10 if q_type != "written" else 15),
            })

        while normalized and len(normalized) < test_request.total_questions:
            src = normalized[len(normalized) % len(normalized)]
            normalized.append({ **src, "id": f"mq-{len(normalized) + 1}" })

        mock_test["questions"] = normalized[: test_request.total_questions]
        mock_test.setdefault("metadata", {})
        mock_test["metadata"]["totalQuestions"] = len(mock_test["questions"])
        
        return SuccessResponse(
            success=True,
            message="Mock test generated successfully",
            data={"mockTest": mock_test}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating mock test: {str(e)}"
        )

@router.get("/results/{topic_id}", response_model=SuccessResponse)
async def get_quiz_results(
    topic_id: str,
    current_user: dict = Depends(get_current_user_from_token)
):
    """Get previous quiz results for a topic"""
    topic = get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Topic not found"
        )
    
    user = current_user
    
    # Mock previous results - in production, these would be stored
    if topic_id in user["completedTopics"]:
        mock_result = {
            "topicId": topic_id,
            "score": 4,
            "totalQuestions": 5,
            "percentage": 80.0,
            "dateTaken": "2026-02-20",
            "timeTaken": 180,  # seconds
            "attempts": 1
        }
        
        return SuccessResponse(
            success=True,
            message="Previous results retrieved",
            data={"results": [mock_result]}
        )
    else:
        return SuccessResponse(
            success=True,
            message="No previous results found", 
            data={"results": []}
        )

@router.get("/performance-analysis", response_model=SuccessResponse)
async def get_performance_analysis(current_user: dict = Depends(get_current_user_from_token)):
    """Get AI-powered analysis of user's quiz performance"""
    user = current_user
    
    try:
        # Prepare user data for analysis
        user_learning_data = {
            "completedTopics": user.get("completedTopics", []),
            "totalScore": user.get("totalScore", 0),
            "preferredStyle": user.get("preferredStyle", "visual"),
            "videosWatched": len(user.get("videosWatched", [])),
            "recentQuizzes": [
                {"topic": "Python Loops", "score": 85, "date": "2026-02-20"},
                {"topic": "Java OOP", "score": 70, "date": "2026-02-18"}
            ]
        }
        
        # Get AI analysis using Gemini
        analysis = await adaptive_engine_service.analyze_learning_progress(user_learning_data)
        
        return SuccessResponse(
            success=True,
            message="Performance analysis completed",
            data={"analysis": analysis}
        )
        
    except Exception as e:
        # Fallback analysis
        fallback_analysis = {
            "strengths": ["Basic programming concepts", "Problem solving"],
            "weaknesses": ["Advanced algorithms", "Complex data structures"],
            "recommendations": [
                "Focus on algorithm practice",
                "Review data structure concepts",
                "Take more intermediate-level quizzes"
            ],
            "nextTopics": ["Binary Trees", "Graph Algorithms", "Dynamic Programming"],
            "studyPlan": "Spend 30 minutes daily on algorithm practice"
        }
        
        return SuccessResponse(
            success=True,
            message="Basic performance analysis completed",
            data={"analysis": fallback_analysis}
        )