"""
Question Generation API Endpoints
Handles on-demand question generation and storage for topics
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import logging
from typing import Optional
from pydantic import BaseModel
from app.services.ai_content_service import AIContentGenerator
from app.core.database import get_database
import asyncio
from bson import ObjectId

logger = logging.getLogger(__name__)

router = APIRouter(tags=["question-generation"])

class GenerateQuestionsRequest(BaseModel):
    """Request to generate questions for a topic"""
    topic_id: str
    topic_name: str
    num_questions: int = 5

class BulkGenerateRequest(BaseModel):
    """Request to generate questions for multiple topics"""
    limit: Optional[int] = None
    overwrite: bool = False  # If true, regenerate even if questions exist

ai_generator = AIContentGenerator()

@router.post("/generate")
async def generate_questions(request: GenerateQuestionsRequest):
    """
    Generate questions for a specific topic and store in database
    
    Args:
        topic_id: MongoDB topic ID
        topic_name: Topic name for question generation
        num_questions: Number of questions to generate (default 5)
    
    Returns:
        Generated questions list with proper structure
    """
    try:
        logger.info(f"Generating {request.num_questions} questions for: {request.topic_name}")
        
        # Check if questions already exist
        db = await get_database()
        topics_collection = db["topics"]
        existing = await topics_collection.find_one({"_id": request.topic_id})
        
        if existing and existing.get("quiz") and len(existing["quiz"]) > 0:
            logger.info(f"Questions already exist for {request.topic_name}")
            return {
                "status": "already_exists",
                "message": f"Topic already has {len(existing['quiz'])} questions",
                "questions": existing["quiz"]
            }
        
        # Generate questions using Gemini
        prompt = f"""TASK: Generate exactly {request.num_questions} professional multiple-choice questions about "{request.topic_name}".

OUTPUT FORMAT - VALID JSON ARRAY ONLY:
[
  {{
    "id": 1,
    "question": "Clear question?",
    "options": ["A", "B", "C", "D"],
    "correctAnswer": "A",
    "correctIdx": 0,
    "explanation": "Why correct.",
    "points": 10,
    "type": "mcq"
  }}
]

REQUIREMENTS:
✓ Exactly {request.num_questions} questions
✓ Each has exactly 4 unique options
✓ correctAnswer is the actual option text
✓ correctIdx is 0-3 (position in options)
✓ Progressive difficulty (easy→medium→hard)
✓ Test understanding, not just facts
✓ Clear, educational explanations

Output ONLY JSON array. No markdown. No explanations.
"""
        
        response = await ai_generator.call_gemini(
            prompt,
            temperature=0.7,
            max_tokens=2048,
            retries=3
        )
        
        if not response:
            raise HTTPException(status_code=500, detail="Failed to generate questions from AI")
        
        # Parse and validate JSON
        import json
        response = response.strip()
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]
        
        questions = json.loads(response.strip())
        
        if not isinstance(questions, list):
            if isinstance(questions, dict) and "questions" in questions:
                questions = questions["questions"]
            else:
                raise ValueError("Invalid JSON structure")
        
        # Validate and normalize each question
        validated = []
        for idx, q in enumerate(questions, 1):
            if not isinstance(q, dict):
                continue
            
            question_text = q.get("question") or q.get("question_text") or ""
            options = q.get("options") or []
            correct_answer = q.get("correctAnswer") or ""
            explanation = q.get("explanation") or ""
            
            # Find correctIdx
            correct_idx = q.get("correctIdx") or 0
            if isinstance(correct_answer, int) and correct_answer < len(options):
                correct_idx = correct_answer
                correct_answer = options[correct_answer]
            elif isinstance(correct_answer, str):
                try:
                    correct_idx = options.index(correct_answer)
                except ValueError:
                    correct_idx = 0
            
            if not question_text or len(options) != 4:
                continue
            
            validated.append({
                "id": idx,
                "question": question_text,
                "options": options,
                "correctAnswer": str(correct_answer),
                "correctIdx": correct_idx,
                "explanation": explanation,
                "points": q.get("points", 10),
                "type": "mcq"
            })
        
        if not validated:
            raise HTTPException(status_code=500, detail="Failed to validate generated questions")
        
        # Store in database
        result = await topics_collection.update_one(
            {"_id": request.topic_id},
            {"$set": {"quiz": validated}}
        )
        
        if result.modified_count == 0:
            logger.warning(f"Topic {request.topic_id} not found or not updated")
        
        logger.info(f"✓ Generated and stored {len(validated)} questions for {request.topic_name}")
        
        return {
            "status": "success",
            "message": f"Generated {len(validated)} questions",
            "topic_name": request.topic_name,
            "questions": validated,
            "count": len(validated)
        }
        
    except Exception as e:
        logger.error(f"Error generating questions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-all")
async def generate_all_questions(
    request: BulkGenerateRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate questions for all topics in background
    
    Args:
        limit: Max topics to process
        overwrite: Regenerate even if questions exist
    
    Returns:
        Job status
    """
    try:
        # Add to background tasks
        background_tasks.add_task(
            bulk_generate_questions,
            limit=request.limit,
            overwrite=request.overwrite
        )
        
        return {
            "status": "started",
            "message": "Question generation started in background",
            "limit": request.limit,
            "overwrite": request.overwrite
        }
        
    except Exception as e:
        logger.error(f"Error starting bulk generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def bulk_generate_questions(limit: Optional[int] = None, overwrite: bool = False):
    """Background task to generate questions for all topics"""
    try:
        db = await get_database()
        topics_collection = db["topics"]
        
        # Get all topics
        pipeline = [{"$project": {"_id": 1, "name": 1, "title": 1}}]
        if limit:
            pipeline.append({"$limit": limit})
        
        all_topics = await topics_collection.aggregate(pipeline).to_list(None)
        logger.info(f"📚 Starting bulk generation for {len(all_topics)} topics")
        
        generated = 0
        failed = 0
        skipped = 0
        
        for idx, topic in enumerate(all_topics, 1):
            topic_id = str(topic["_id"])
            topic_name = topic.get("name") or topic.get("title") or "Unknown"
            
            # Check if skip
            if not overwrite:
                existing = await topics_collection.find_one({"_id": topic["_id"]})
                if existing and existing.get("quiz"):
                    logger.info(f"[{idx}/{len(all_topics)}] ⏭️  Skipping {topic_name}")
                    skipped += 1
                    continue
            
            # Generate
            try:
                questions = await generate_single_topic_questions(topic_id, topic_name)
                if questions:
                    await topics_collection.update_one(
                        {"_id": topic["_id"]},
                        {"$set": {"quiz": questions}}
                    )
                    logger.info(f"[{idx}/{len(all_topics)}] ✅ {topic_name} ({len(questions)} Q's)")
                    generated += 1
                else:
                    logger.error(f"[{idx}/{len(all_topics)}] ❌ {topic_name}")
                    failed += 1
            except Exception as e:
                logger.error(f"[{idx}/{len(all_topics)}] Failed for {topic_name}: {e}")
                failed += 1
            
            # Rate limiting
            await asyncio.sleep(2)
        
        logger.info(f"\n📊 BULK GENERATION COMPLETE")
        logger.info(f"✅ Generated: {generated} | ⏭️ Skipped: {skipped} | ❌ Failed: {failed}")
        
    except Exception as e:
        logger.error(f"Bulk generation error: {e}")

async def generate_single_topic_questions(topic_id: str, topic_name: str) -> list:
    """Generate questions for a single topic"""
    prompt = f"""Generate exactly 5 multiple-choice questions for: {topic_name}

OUTPUT - JSON ARRAY ONLY:
[{{"id":1,"question":"Q?","options":["A","B","C","D"],"correctAnswer":"A","correctIdx":0,"explanation":"Why.","points":10,"type":"mcq"}}]

Requirements:
- 5 questions, each with 4 unique options
- correctAnswer = option text exactly
- correctIdx = 0,1,2,3
- Progressive difficulty
- Clear explanations
- MCQ type

Output ONLY "[{{...}}]" - no markdown, no text.
"""
    
    try:
        response = await ai_generator.call_gemini(prompt, temperature=0.7, max_tokens=1500)
        
        if not response:
            return []
        
        import json
        response = response.strip()
        if "```" in response:
            response = response.split("```")[1] if "```" in response else response
            if "json" in response:
                response = response.split("json")[1]
        response = response.strip("` \n")
        
        questions = json.loads(response)
        if not isinstance(questions, list):
            return []
        
        # Validate
        validated = []
        for idx, q in enumerate(questions, 1):
            if isinstance(q, dict) and q.get("question") and q.get("options"):
                validated.append({
                    "id": idx,
                    "question": q.get("question", ""),
                    "options": q.get("options", [])[:4],
                    "correctAnswer": str(q.get("correctAnswer", "")),
                    "correctIdx": int(q.get("correctIdx", 0)),
                    "explanation": q.get("explanation", ""),
                    "points": q.get("points", 10),
                    "type": "mcq"
                })
        
        return validated[:5]
    except:
        return []

@router.get("/topic/{topic_id}")
async def get_topic_questions(topic_id: str):
    """
    Get all questions for a topic
    
    Returns formatted questions with clear structure
    """
    try:
        from bson import ObjectId
        db = await get_database()
        topics_collection = db["topics"]
        
        # Try to parse as ObjectId
        try:
            topic_obj_id = ObjectId(topic_id)
        except:
            topic_obj_id = topic_id
        
        topic = await topics_collection.find_one({"_id": topic_obj_id})
        
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        questions = topic.get("quiz", [])
        
        if not questions:
            return {
                "status": "no_questions",
                "message": "No questions available for this topic",
                "topic_id": topic_id,
                "topic_name": topic.get("name") or topic.get("title"),
                "questions": []
            }
        
        # Format for display
        formatted_questions = []
        for q in questions:
            formatted_questions.append({
                "id": q.get("id", 0),
                "question": q.get("question", ""),
                "options": q.get("options", []),
                "correctAnswer": q.get("correctAnswer", ""),
                "correctIdx": q.get("correctIdx", 0),
                "explanation": q.get("explanation", ""),
                "points": q.get("points", 10),
                "type": q.get("type", "mcq")
            })
        
        return {
            "status": "success",
            "topic_id": topic_id,
            "topic_name": topic.get("name") or topic.get("title"),
            "total_questions": len(formatted_questions),
            "questions": formatted_questions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching questions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test/{topic_id}")
async def test_question_generation(topic_id: str, topic_name: str):
    """
    Test generate questions for a specific topic
    Useful for debugging and testing generation quality
    """
    return await generate_questions(GenerateQuestionsRequest(
        topic_id=topic_id,
        topic_name=topic_name,
        num_questions=5
    ))
