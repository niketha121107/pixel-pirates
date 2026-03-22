#!/usr/bin/env python
"""
AI-Powered Study Materials Route
Generates comprehensive learning materials using Gemini AI
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from app.core.auth import get_current_user_from_token
from app.models import SuccessResponse
from app.services.ai_content_service import ai_generator
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/study-material/{topic_id}", response_model=SuccessResponse)
async def get_ai_study_material(
    topic_id: str,
    current_user: dict = Depends(get_current_user_from_token)
):
    """Get AI-generated study material for a topic"""
    try:
        from app.data import get_topic_by_id
        topic = get_topic_by_id(topic_id)
        
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        topic_name = topic.get("topicName") or topic.get("name", "Programming Concept")
        language = topic.get("language", "Python")
        difficulty = topic.get("difficulty", "Intermediate")
        
        logger.info(f"Generating study material for {topic_name}")
        
        # Generate comprehensive study material
        result = await ai_generator.generate_study_material(
            topic_name=topic_name,
            language=language,
            difficulty=difficulty
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail="Failed to generate study material")
        
        material = result.get("data", {})
        
        return SuccessResponse(
            success=True,
            message="AI-generated study material created",
            data={
                "topicId": topic_id,
                "topicName": topic_name,
                "studyMaterial": {
                    "title": topic_name,
                    "overview": material.get("overview", ""),
                    "explanation": material.get("explanation", ""),
                    "syntax": material.get("syntax", ""),
                    "codeExample": material.get("example", ""),
                    "advantages": material.get("advantages", "").split('\n') if material.get("advantages") else [],
                    "disadvantages": material.get("disadvantages", "").split('\n') if material.get("disadvantages") else [],
                    "realWorldApplication": material.get("realWorldApplication", ""),
                    "type": "comprehensive",
                    "generatedAt": result.get("generatedAt")
                }
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating study material: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/explanations/{topic_id}", response_model=SuccessResponse)
async def get_ai_explanations(
    topic_id: str,
    styles: str = Query("simplified,logical,visual,analogy"),
    current_user: dict = Depends(get_current_user_from_token)
):
    """Get AI-generated explanations in multiple styles"""
    try:
        from app.data import get_topic_by_id
        topic = get_topic_by_id(topic_id)
        
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        topic_name = topic.get("topicName") or topic.get("name", "Programming Concept")
        
        # Parse requested styles
        requested_styles = [s.strip() for s in styles.split(",")]
        requested_styles = [s for s in requested_styles if s in ["simplified", "logical", "visual", "analogy"]]
        
        if not requested_styles:
            requested_styles = ["simplified", "logical", "visual", "analogy"]
        
        logger.info(f"Generating {len(requested_styles)} explanations for {topic_name}")
        
        # Generate explanations
        explanations = await ai_generator.generate_explanations(
            topic_name=topic_name,
            styles=requested_styles
        )
        
        # Format for response
        explanations_array = [
            {
                "style": style,
                "title": explanations[style].get("title", f"{style.capitalize()} Explanation"),
                "content": explanations[style].get("content", ""),
                "codeExample": ""
            }
            for style in requested_styles
            if style in explanations
        ]
        
        return SuccessResponse(
            success=True,
            message=f"Generated {len(explanations_array)} AI explanations",
            data={
                "topicId": topic_id,
                "topicName": topic_name,
                "explanations": explanations_array,
                "totalStyles": len(explanations_array)
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating explanations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/full-content/{topic_id}", response_model=SuccessResponse)
async def get_full_ai_content(
    topic_id: str,
    include_quiz: bool = Query(True),
    quiz_questions: int = Query(5, ge=1, le=20),
    current_user: dict = Depends(get_current_user_from_token)
):
    """Get complete AI-generated learning content for a topic"""
    try:
        from app.data import get_topic_by_id
        topic = get_topic_by_id(topic_id)
        
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        topic_name = topic.get("topicName") or topic.get("name", "Programming Concept")
        language = topic.get("language", "Python")
        difficulty = topic.get("difficulty", "Intermediate")
        
        logger.info(f"Generating full content package for {topic_name}")
        
        # Generate all content in parallel (conceptually)
        study_result = await ai_generator.generate_study_material(topic_name, language, difficulty)
        explanations = await ai_generator.generate_explanations(topic_name)
        questions = await ai_generator.generate_quiz_questions(topic_name, quiz_questions, "mixed") if include_quiz else []
        
        return SuccessResponse(
            success=True,
            message="Complete AI-generated learning package created",
            data={
                "topicId": topic_id,
                "topicName": topic_name,
                "language": language,
                "difficulty": difficulty,
                "studyMaterial": study_result.get("data", {}) if study_result.get("success") else {},
                "explanations": explanations,
                "quiz": {
                    "questions": questions,
                    "totalQuestions": len(questions),
                    "isGenerated": True
                }
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating full content: {e}")
        raise HTTPException(status_code=500, detail=str(e))
