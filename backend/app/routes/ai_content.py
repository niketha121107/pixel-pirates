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
        
        logger.info(f"[StudyMaterial] Fetching topic: {topic_id}")
        
        # Query for the topic using the data layer
        topic = get_topic_by_id(topic_id)
        
        if not topic:
            logger.error(f"[StudyMaterial] Topic not found: {topic_id}")
            raise HTTPException(status_code=404, detail="Topic not found")
        
        topic_name = topic.get("topicName") or topic.get("name", "Programming Concept")
        language = topic.get("language", "Python")
        difficulty = topic.get("difficulty", "Intermediate")
        
        logger.info(f"[StudyMaterial] Generating for: {topic_name} ({language}, {difficulty})")
        
        # Try to generate comprehensive study material
        try:
            result = await ai_generator.generate_study_material(
                topic_name=topic_name,
                language=language,
                difficulty=difficulty
            )
        except Exception as ai_error:
            logger.warning(f"[StudyMaterial] AI generation failed with exception: {type(ai_error).__name__}: {str(ai_error)}")
            # Return empty successful response so frontend can fall back to database
            return SuccessResponse(
                success=True,
                message="Study material not available from AI, check database",
                data={"topicId": topic_id, "topicName": topic_name, "studyMaterial": {}}
            )
        
        # If AI generation failed, return a basic structure (frontend will fallback to database)
        if not result.get("success"):
            error_msg = result.get("error", "AI generation unavailable")
            logger.warning(f"[StudyMaterial] Generation failed: {error_msg} - returning empty response for fallback")
            # Return empty successful response so frontend can fall back to database
            return SuccessResponse(
                success=True,
                message="Study material not available from AI, check database",
                data={"topicId": topic_id, "topicName": topic_name, "studyMaterial": {}}
            )
        
        material = result.get("data", {})
        logger.info(f"[StudyMaterial] Successfully generated for {topic_name}")
        
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
        logger.error(f"[StudyMaterial] Exception: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/explanations/{topic_id}", response_model=SuccessResponse)
async def get_ai_explanations(
    topic_id: str,
    styles: str = Query("simplified,logical,visual,analogy"),
    current_user: dict = Depends(get_current_user_from_token)
):
    """Get AI-generated explanations in multiple styles"""
    try:
        from app.core.database import db
        from bson import ObjectId
        
        # Query MongoDB directly for the topic
        topic = None
        if db.database:
            topics_collection = db.database["topics"]
            try:
                # Try to find by ObjectId first
                topic = topics_collection.find_one({"_id": ObjectId(topic_id) if len(topic_id) == 24 else topic_id})
            except:
                # If that fails, try string lookup
                topic = topics_collection.find_one({"_id": topic_id})
        
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
        try:
            explanations = await ai_generator.generate_explanations(
                topic_name=topic_name,
                styles=requested_styles
            )
        except Exception as ai_error:
            logger.warning(f"[Explanations] AI generation failed: {type(ai_error).__name__}: {str(ai_error)}")
            return SuccessResponse(
                success=True,
                message="Explanations not available from AI",
                data={
                    "topicId": topic_id,
                    "topicName": topic_name,
                    "explanations": [],
                    "totalStyles": 0
                }
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
            if style in explanations and explanations[style].get("content", "").strip()
        ]
        
        # If no explanations generated, return empty response for fallback
        if not explanations_array:
            logger.warning(f"[Explanations] No explanations generated for {topic_name}")
            return SuccessResponse(
                success=True,
                message="Explanations not available from AI",
                data={
                    "topicId": topic_id,
                    "topicName": topic_name,
                    "explanations": [],
                    "totalStyles": 0
                }
            )
        
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
        try:
            study_result = await ai_generator.generate_study_material(topic_name, language, difficulty)
        except Exception as e:
            logger.warning(f"[FullContent] Study material generation failed: {e}")
            study_result = {"success": False}
        
        try:
            explanations = await ai_generator.generate_explanations(topic_name)
        except Exception as e:
            logger.warning(f"[FullContent] Explanations generation failed: {e}")
            explanations = {}
        
        try:
            questions = await ai_generator.generate_quiz_questions(topic_name, quiz_questions, "mixed") if include_quiz else []
        except Exception as e:
            logger.warning(f"[FullContent] Quiz generation failed: {e}")
            questions = []
        
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
                    "totalQuestions": len(questions) if questions else 0,
                    "isGenerated": True
                }
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating full content: {e}")
        raise HTTPException(status_code=500, detail=str(e))
