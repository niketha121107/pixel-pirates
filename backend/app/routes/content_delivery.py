"""
Extended API Routes for Generated Content
Handles retrieval of videos, explanations, PDFs, and complete topic data
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from bson import ObjectId
from app.core.auth import get_current_user_from_token
from app.core.database import db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/content", tags=["Generated Content"])

# ── Video Routes ────────────────────────────────────────────────
@router.get("/videos/{topic_id}")
async def get_topic_videos(
    topic_id: str,
    current_user: dict = Depends(get_current_user_from_token)
) -> Dict[str, Any]:
    """
    Get recommended YouTube videos for a topic.
    Returns list of highly-recommended videos with metadata.
    """
    try:
        if db.database is None:
            raise HTTPException(status_code=503, detail="Database not available")
        
        topics_col = db.database["topics"]
        
        # Find topic
        topic = await topics_col.find_one({
            "_id": ObjectId(topic_id) if len(topic_id) == 24 else topic_id
        })
        
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        videos = topic.get("recommendedVideos", [])
        
        return {
            "success": True,
            "topic_id": topic_id,
            "topic_name": topic.get("topicName", ""),
            "total_videos": len(videos),
            "videos": videos,
            "generated_at": topic.get("contentGeneratedAt")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching videos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/videos/search")
async def search_videos_by_topic(
    topic_name: str = Query(..., min_length=2),
    language: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user_from_token)
) -> Dict[str, Any]:
    """
    Search and get videos for topics by name.
    """
    try:
        if db.database is None:
            raise HTTPException(status_code=503, detail="Database not available")
        
        topics_col = db.database["topics"]
        
        # Build query
        query = {
            "topicName": {"$regex": topic_name, "$options": "i"}
        }
        
        if language:
            query["language"] = language
        
        # Find topics
        cursor = topics_col.find(query)
        topics = await cursor.to_list(length=50)
        
        all_videos = []
        for topic in topics:
            videos = topic.get("recommendedVideos", [])
            for video in videos:
                video["topic"] = topic.get("topicName", "")
                video["language"] = topic.get("language", "")
                all_videos.append(video)
        
        return {
            "success": True,
            "search_query": topic_name,
            "total_videos": len(all_videos),
            "total_topics": len(topics),
            "videos": all_videos[:50]  # Limit to 50
        }
        
    except Exception as e:
        logger.error(f"Error searching videos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Explanation Routes ──────────────────────────────────────────
@router.get("/explanations/{topic_id}")
async def get_topic_explanations(
    topic_id: str,
    style: Optional[str] = Query(None, description="Filter by explanation style: visual, simplified, logical, analogy"),
    current_user: dict = Depends(get_current_user_from_token)
) -> Dict[str, Any]:
    """
    Get all 4 types of explanations for a topic.
    Optionally filter by specific explanation style.
    """
    try:
        if db.database is None:
            raise HTTPException(status_code=503, detail="Database not available")
        
        topics_col = db.database["topics"]
        
        # Find topic
        topic = await topics_col.find_one({
            "_id": ObjectId(topic_id) if len(topic_id) == 24 else topic_id
        })
        
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        explanations = topic.get("explanations", [])
        
        # Filter by style if requested
        if style:
            explanations = [e for e in explanations if e.get("style") == style]
        
        return {
            "success": True,
            "topic_id": topic_id,
            "topic_name": topic.get("topicName", ""),
            "total_explanations": len(explanations),
            "explanation_styles": list(set(e.get("style") for e in topic.get("explanations", []))),
            "explanations": explanations,
            "generated_at": topic.get("contentGeneratedAt")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching explanations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/explanations/by-style/{style}")
async def get_explanations_by_style(
    style: str,
    language: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user_from_token)
) -> Dict[str, Any]:
    """
    Get all explanations of a specific style across topics.
    Useful for learning a particular explanation style.
    """
    try:
        if db.database is None:
            raise HTTPException(status_code=503, detail="Database not available")
        
        valid_styles = ["visual", "simplified", "logical", "analogy"]
        if style not in valid_styles:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid style. Must be one of: {', '.join(valid_styles)}"
            )
        
        topics_col = db.database["topics"]
        
        # Build query
        query = {
            "explanations": {"$elemMatch": {"style": style}}
        }
        
        if language:
            query["language"] = language
        
        # Find topics
        cursor = topics_col.find(query).limit(100)
        topics = await cursor.to_list(length=100)
        
        all_explanations = []
        for topic in topics:
            explanations = topic.get("explanations", [])
            for exp in explanations:
                if exp.get("style") == style:
                    exp["topic"] = topic.get("topicName", "")
                    exp["topic_id"] = str(topic.get("_id", ""))
                    exp["language"] = topic.get("language", "")
                    all_explanations.append(exp)
        
        return {
            "success": True,
            "style": style,
            "total_explanations": len(all_explanations),
            "total_topics": len(topics),
            "explanations": all_explanations
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching explanations by style: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── PDF Routes ─────────────────────────────────────────────────
@router.get("/pdf/{topic_id}")
async def get_topic_pdf_info(
    topic_id: str,
    current_user: dict = Depends(get_current_user_from_token)
) -> Dict[str, Any]:
    """
    Get PDF information for a topic.
    Returns PDF metadata and download info.
    """
    try:
        if db.database is None:
            raise HTTPException(status_code=503, detail="Database not available")
        
        topics_col = db.database["topics"]
        
        # Find topic
        topic = await topics_col.find_one({
            "_id": ObjectId(topic_id) if len(topic_id) == 24 else topic_id
        })
        
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        pdf_path = topic.get("pdfPath")
        
        if not pdf_path:
            return {
                "success": False,
                "message": "PDF not yet generated for this topic",
                "topic_id": topic_id,
                "topic_name": topic.get("topicName", "")
            }
        
        return {
            "success": True,
            "topic_id": topic_id,
            "topic_name": topic.get("topicName", ""),
            "pdf_path": pdf_path,
            "pdf_filename": pdf_path.split("/")[-1],
            "generated_at": topic.get("contentGeneratedAt"),
            "download_url": f"/api/content/pdf/download/{topic_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching PDF info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pdf/download/{topic_id}")
async def download_topic_pdf(
    topic_id: str,
    current_user: dict = Depends(get_current_user_from_token)
):
    """
    Download PDF for a topic.
    """
    try:
        if db.database is None:
            raise HTTPException(status_code=503, detail="Database not available")
        
        topics_col = db.database["topics"]
        
        # Find topic
        topic = await topics_col.find_one({
            "_id": ObjectId(topic_id) if len(topic_id) == 24 else topic_id
        })
        
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        pdf_path = topic.get("pdfPath")
        
        if not pdf_path:
            raise HTTPException(status_code=404, detail="PDF not found for this topic")
        
        import os
        from fastapi.responses import FileResponse
        
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail="PDF file not found on server")
        
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"{topic.get('topicName', 'study')}.pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Mock Test Routes ────────────────────────────────────────────
@router.get("/mock-tests/{topic_id}")
async def get_topic_mock_test(
    topic_id: str,
    current_user: dict = Depends(get_current_user_from_token)
) -> Dict[str, Any]:
    """
    Get mock test questions for a topic.
    Returns complete test with all questions.
    """
    try:
        if db.database is None:
            raise HTTPException(status_code=503, detail="Database not available")
        
        # Get topic first
        topics_col = db.database["topics"]
        topic = await topics_col.find_one({
            "_id": ObjectId(topic_id) if len(topic_id) == 24 else topic_id
        })
        
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        # Get mock test from separate collection
        mock_tests_col = db.database["mockTests"]
        mock_test = await mock_tests_col.find_one({
            "topicId": str(topic_id)
        })
        
        if not mock_test:
            # Return questions from topic
            questions = topic.get("mockQuestions", [])
            
            return {
                "success": True,
                "topic_id": topic_id,
                "topic_name": topic.get("topicName", ""),
                "total_questions": len(questions),
                "duration_minutes": len(questions) * 2,
                "questions": questions
            }
        
        return {
            "success": True,
            "mock_test_id": str(mock_test.get("_id", "")),
            "topic_id": topic_id,
            "topic_name": mock_test.get("topicName", ""),
            "total_questions": mock_test.get("totalQuestions", 0),
            "duration_minutes": mock_test.get("duration", 0),
            "difficulty": mock_test.get("difficulty", "mixed"),
            "questions": mock_test.get("questions", []),
            "created_at": mock_test.get("createdAt")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching mock test: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mock-tests/search")
async def search_mock_tests(
    topic_name: str = Query(..., min_length=2),
    language: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user_from_token)
) -> Dict[str, Any]:
    """
    Search for mock tests by topic name.
    """
    try:
        if db.database is None:
            raise HTTPException(status_code=503, detail="Database not available")
        
        mock_tests_col = db.database["mockTests"]
        
        # Build query
        query = {
            "topicName": {"$regex": topic_name, "$options": "i"}
        }
        
        # Find tests
        cursor = mock_tests_col.find(query).limit(50)
        tests = await cursor.to_list(length=50)
        
        return {
            "success": True,
            "search_query": topic_name,
            "total_tests": len(tests),
            "tests": [
                {
                    "test_id": str(t.get("_id", "")),
                    "topic_name": t.get("topicName", ""),
                    "total_questions": t.get("totalQuestions", 0),
                    "duration_minutes": t.get("duration", 0),
                    "difficulty": t.get("difficulty", ""),
                    "created_at": t.get("createdAt")
                }
                for t in tests
            ]
        }
        
    except Exception as e:
        logger.error(f"Error searching mock tests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Complete Topic Data Route ───────────────────────────────────
@router.get("/complete/{topic_id}")
async def get_complete_topic_data(
    topic_id: str,
    current_user: dict = Depends(get_current_user_from_token)
) -> Dict[str, Any]:
    """
    Get complete topic data including videos, explanations, PDF, and mock test.
    This is the main endpoint for loading a full study session.
    """
    try:
        if db.database is None:
            raise HTTPException(status_code=503, detail="Database not available")
        
        topics_col = db.database["topics"]
        mock_tests_col = db.database["mockTests"]
        
        # Find topic
        topic = await topics_col.find_one({
            "_id": ObjectId(topic_id) if len(topic_id) == 24 else topic_id
        })
        
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        # Find mock test
        mock_test = await mock_tests_col.find_one({"topicId": str(topic_id)})
        
        # Compile complete data
        data = {
            "success": True,
            "topic": {
                "id": str(topic.get("_id", "")),
                "name": topic.get("topicName", ""),
                "language": topic.get("language", ""),
                "difficulty": topic.get("difficulty", ""),
                "overview": topic.get("overview", "")
            },
            "videos": {
                "total": len(topic.get("recommendedVideos", [])),
                "items": topic.get("recommendedVideos", [])
            },
            "explanations": {
                "total": len(topic.get("explanations", [])),
                "styles": list(set(
                    e.get("style") for e in topic.get("explanations", [])
                )),
                "items": topic.get("explanations", [])
            },
            "pdf": {
                "available": bool(topic.get("pdfPath")),
                "path": topic.get("pdfPath"),
                "download_url": f"/api/content/pdf/download/{topic_id}" if topic.get("pdfPath") else None
            },
            "mock_test": {
                "total_questions": 0,
                "duration_minutes": 0,
                "questions": []
            },
            "metadata": {
                "generated_at": topic.get("contentGeneratedAt"),
                "content_status": topic.get("contentStatus", "")
            }
        }
        
        # Add mock test data
        if mock_test:
            data["mock_test"] = {
                "test_id": str(mock_test.get("_id", "")),
                "total_questions": mock_test.get("totalQuestions", 0),
                "duration_minutes": mock_test.get("duration", 0),
                "difficulty": mock_test.get("difficulty", ""),
                "questions": mock_test.get("questions", [])
            }
        
        return data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching complete topic data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Statistics Routes ────────────────────────────────────────────
@router.get("/statistics")
async def get_content_statistics(
    current_user: dict = Depends(get_current_user_from_token)
) -> Dict[str, Any]:
    """
    Get statistics about generated content.
    Total topics, videos, explanations, PDFs, mock tests generated.
    """
    try:
        if db.database is None:
            raise HTTPException(status_code=503, detail="Database not available")
        
        topics_col = db.database["topics"]
        mock_tests_col = db.database["mockTests"]
        
        # Count statistics
        total_topics = await topics_col.count_documents({})
        topics_with_content = await topics_col.count_documents({
            "contentStatus": "complete"
        })
        topics_with_videos = await topics_col.count_documents({
            "recommendedVideos": {"$ne": []}
        })
        topics_with_explanations = await topics_col.count_documents({
            "explanations": {"$ne": []}
        })
        topics_with_pdfs = await topics_col.count_documents({
            "pdfPath": {"$ne": None}
        })
        total_mock_tests = await mock_tests_col.count_documents({})
        
        return {
            "success": True,
            "statistics": {
                "total_topics": total_topics,
                "topics_with_complete_content": topics_with_content,
                "topics_with_videos": topics_with_videos,
                "topics_with_explanations": topics_with_explanations,
                "topics_with_pdfs": topics_with_pdfs,
                "total_mock_tests": total_mock_tests,
                "completion_percentage": round(
                    (topics_with_content / max(total_topics, 1)) * 100, 2
                )
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Admin PDF Generation Routes ──────────────────────────────────
@router.post("/admin/generate-pdf/{topic_id}")
async def admin_generate_pdf_for_topic(
    topic_id: str,
    current_user: dict = Depends(get_current_user_from_token)
) -> Dict[str, Any]:
    """
    [ADMIN ONLY] Generate PDF for a specific topic.
    Updates the topic's pdfPath field in database.
    """
    try:
        # Basic auth check - in production, verify user roles
        if db.database is None:
            raise HTTPException(status_code=503, detail="Database not available")
        
        topics_col = db.database["topics"]
        
        # Find topic
        topic = await topics_col.find_one({
            "_id": ObjectId(topic_id) if len(topic_id) == 24 else topic_id
        })
        
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        # Generate PDF
        from app.services.topic_pdf_generator import topic_pdf_generator
        import os
        
        pdf_dir = os.path.join(
            os.path.dirname(__file__),
            "../../storage/pdfs"
        )
        os.makedirs(pdf_dir, exist_ok=True)
        
        topic_name_safe = topic.get('name', 'topic').replace(' ', '_').lower()
        pdf_filename = f"{topic_name_safe}_{topic_id}.pdf"
        pdf_path = os.path.join(pdf_dir, pdf_filename)
        
        success = topic_pdf_generator.generate_topic_pdf(topic, pdf_path)
        
        if success:
            # Update database with PDF path
            await topics_col.update_one(
                {"_id": ObjectId(topic_id) if len(topic_id) == 24 else topic_id},
                {
                    "$set": {
                        "pdfPath": pdf_path,
                        "pdfGeneratedAt": datetime.now().isoformat()
                    }
                }
            )
            
            return {
                "success": True,
                "message": f"PDF generated for topic: {topic.get('name', 'Unknown')}",
                "topic_id": topic_id,
                "topic_name": topic.get('name', ''),
                "pdf_path": pdf_path,
                "download_url": f"/api/content/pdf/download/{topic_id}"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate PDF")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PDF: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/generate-all-pdfs")
async def admin_generate_all_pdfs(
    current_user: dict = Depends(get_current_user_from_token)
) -> Dict[str, Any]:
    """
    [ADMIN ONLY] Generate PDFs for ALL topics.
    This is a bulk operation that may take time.
    Returns summary of generation results.
    """
    try:
        if db.database is None:
            raise HTTPException(status_code=503, detail="Database not available")
        
        topics_col = db.database["topics"]
        
        # Get all topics
        cursor = topics_col.find({})
        topics = await cursor.to_list(length=None)
        
        logger.info(f"Starting PDF generation for {len(topics)} topics...")
        
        from app.services.topic_pdf_generator import topic_pdf_generator
        import os
        
        pdf_dir = os.path.join(
            os.path.dirname(__file__),
            "../../storage/pdfs"
        )
        os.makedirs(pdf_dir, exist_ok=True)
        
        generated = 0
        failed = 0
        skipped = 0
        
        for idx, topic in enumerate(topics, 1):
            try:
                topic_id = str(topic.get('_id', ''))
                topic_name = topic.get('name', 'topic')
                
                # Skip if PDF already exists
                if topic.get('pdfPath'):
                    logger.info(f"[{idx}/{len(topics)}] Skipping {topic_name} - PDF already exists")
                    skipped += 1
                    continue
                
                # Generate PDF
                topic_name_safe = topic_name.replace(' ', '_').lower()
                pdf_filename = f"{topic_name_safe}_{topic_id}.pdf"
                pdf_path = os.path.join(pdf_dir, pdf_filename)
                
                success = topic_pdf_generator.generate_topic_pdf(topic, pdf_path)
                
                if success:
                    # Update database
                    await topics_col.update_one(
                        {"_id": ObjectId(topic_id) if len(topic_id) == 24 else topic_id},
                        {
                            "$set": {
                                "pdfPath": pdf_path,
                                "pdfGeneratedAt": datetime.now().isoformat()
                            }
                        }
                    )
                    logger.info(f"[{idx}/{len(topics)}] ✅ Generated PDF for: {topic_name}")
                    generated += 1
                else:
                    logger.warning(f"[{idx}/{len(topics)}] ❌ Failed to generate PDF for: {topic_name}")
                    failed += 1
                    
            except Exception as e:
                logger.error(f"[{idx}/{len(topics)}] Error generating PDF for {topic.get('name', 'unknown')}: {e}")
                failed += 1
        
        logger.info(f"PDF generation complete: {generated} generated, {failed} failed, {skipped} skipped")
        
        return {
            "success": True,
            "message": "PDF generation completed",
            "statistics": {
                "total_topics": len(topics),
                "pdfs_generated": generated,
                "pdfs_failed": failed,
                "pdfs_skipped": skipped,
                "pdf_directory": pdf_dir
            }
        }
        
    except Exception as e:
        logger.error(f"Error in batch PDF generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

