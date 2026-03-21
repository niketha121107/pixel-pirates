"""
Convenient endpoints for retrieving topic PDFs and study materials with PDFs
Add these endpoints to app/routes/study_materials.py
"""

# Add this to the imports section if not already there:
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse, JSONResponse
from typing import Dict, Any, List
import os
from bson import ObjectId

# Add these endpoints to router:

@router.get("/topic/{topic_name}/pdf")
async def get_topic_pdf_info(
    topic_name: str,
    current_user: dict = Depends(get_current_user_from_token)
) -> Dict[str, Any]:
    """Get PDF information for a specific topic by name"""
    try:
        if not db.database:
            raise HTTPException(status_code=500, detail="Database not available")
        
        topics_collection = db.database["topics"]
        
        # Find topic by name
        topic = await topics_collection.find_one({
            "$or": [
                {"topicName": topic_name},
                {"name": topic_name}
            ]
        })
        
        if not topic:
            raise HTTPException(status_code=404, detail=f"Topic '{topic_name}' not found")
        
        pdf_path = topic.get("pdf_path")
        pdf_filename = topic.get("pdf_filename")
        
        if not pdf_path or not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail=f"PDF not available for '{topic_name}'")
        
        return {
            "success": True,
            "topic": topic_name,
            "pdf_filename": pdf_filename,
            "pdf_download_url": f"/api/study-materials/pdf/{pdf_filename}",
            "pdf_size_kb": round(os.path.getsize(pdf_path) / 1024, 2),
            "available": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        _log.error(f"Error getting PDF info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all-topics/pdf-info")
async def get_all_topics_pdf_info(
    current_user: dict = Depends(get_current_user_from_token)
) -> Dict[str, Any]:
    """Get PDF information for all topics"""
    try:
        if not db.database:
            raise HTTPException(status_code=500, detail="Database not available")
        
        topics_collection = db.database["topics"]
        
        # Get all topics with PDF info
        topics_with_pdf = list(await topics_collection.find(
            {"pdf_path": {"$exists": True}},
            {"topicName": 1, "pdf_filename": 1, "pdf_path": 1}
        ).to_list(None))
        
        topics_without_pdf = list(await topics_collection.find(
            {"pdf_path": {"$exists": False}},
            {"topicName": 1}
        ).to_list(None))
        
        pdf_info = []
        for topic in topics_with_pdf:
            pdf_path = topic.get("pdf_path", "")
            pdf_filename = topic.get("pdf_filename", "")
            
            if os.path.exists(pdf_path):
                pdf_info.append({
                    "topic": topic.get("topicName") or topic.get("name"),
                    "pdf_filename": pdf_filename,
                    "pdf_download_url": f"/api/study-materials/pdf/{pdf_filename}",
                    "pdf_size_kb": round(os.path.getsize(pdf_path) / 1024, 2)
                })
        
        return {
            "success": True,
            "total_topics": len(topics_with_pdf) + len(topics_without_pdf),
            "topics_with_pdf": len(topics_with_pdf),
            "topics_without_pdf": len(topics_without_pdf),
            "coverage": f"{100*len(topics_with_pdf)/(len(topics_with_pdf) + len(topics_without_pdf)):.1f}%",
            "pdfs": pdf_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        _log.error(f"Error getting all PDF info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/topics-without-pdf")
async def get_topics_without_pdf(
    current_user: dict = Depends(get_current_user_from_token)
) -> Dict[str, Any]:
    """Get list of topics that don't have PDFs yet"""
    try:
        if not db.database:
            raise HTTPException(status_code=500, detail="Database not available")
        
        topics_collection = db.database["topics"]
        
        # Get topics without PDF
        topics = list(await topics_collection.find(
            {"pdf_path": {"$exists": False}},
            {"topicName": 1}
        ).to_list(None))
        
        topic_names = [topic.get("topicName") or topic.get("name") for topic in topics]
        
        return {
            "success": True,
            "count": len(topic_names),
            "topics": topic_names
        }
        
    except HTTPException:
        raise
    except Exception as e:
        _log.error(f"Error getting topics without PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))
