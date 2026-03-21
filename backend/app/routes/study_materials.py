"""
Routes for Study Material Generation and PDF Management
"""

import os
import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
from app.core.auth import get_current_user_from_token
from app.services.study_material_service import study_material_generator
from app.services.pdf_generator_service import pdf_generator
from app.core.database import db
import asyncio

_log = logging.getLogger(__name__)
router = APIRouter(prefix="/api/study-materials", tags=["Study Materials"])

# Define PDF storage directory
PDF_STORAGE_DIR = os.path.join(os.path.dirname(__file__), "../../storage/pdfs")
os.makedirs(PDF_STORAGE_DIR, exist_ok=True)


@router.post("/generate/{topic_id}")
async def generate_study_material(
    topic_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user_from_token)
) -> Dict[str, Any]:
    """Generate study material with all 4 explanation levels for a topic"""
    try:
        # Get topic from database
        topic_name = None
        
        if db.database:
            topics_collection = db.database["topics"]
            try:
                from bson import ObjectId
                topic = await topics_collection.find_one({"_id": ObjectId(topic_id) if len(topic_id) == 24 else topic_id})
                if topic:
                    topic_name = topic.get("topicName") or topic.get("name")
            except:
                pass
        
        # If no topic found, return error
        if not topic_name:
            raise HTTPException(status_code=404, detail="Topic not found")
        
        if not topic_name:
            raise HTTPException(status_code=404, detail=f"Topic {topic_id} not found")
        
        _log.info(f"Generating study material for topic: {topic_name}")
        
        # Generate study material (async)
        study_material = await study_material_generator.generate_study_material(topic_name)
        
        if not study_material:
            raise HTTPException(status_code=500, detail="Failed to generate study material")
        
        # Save to database
        if db.database:
            try:
                materials_collection = db.database["study_materials"]
                
                # Check if exists
                existing = await materials_collection.find_one({
                    "topic": topic_name,
                    "user_id": current_user.get("_id")
                })
                
                if existing:
                    # Update existing
                    await materials_collection.update_one(
                        {"_id": existing["_id"]},
                        {"$set": study_material}
                    )
                    material_id = str(existing["_id"])
                else:
                    # Insert new
                    study_material["user_id"] = current_user.get("_id")
                    study_material["topic_id"] = topic_id
                    result = await materials_collection.insert_one(study_material)
                    material_id = str(result.inserted_id)
                    
                _log.info(f"Study material saved to database: {material_id}")
            except Exception as e:
                _log.warning(f"Could not save to database: {e}")
                material_id = None
        else:
            material_id = None
        
        # Generate PDF in background
        pdf_filename = f"study_{topic_id}_{current_user.get('_id', 'user')}.pdf"
        pdf_path = os.path.join(PDF_STORAGE_DIR, pdf_filename)
        background_tasks.add_task(pdf_generator.generate_pdf, study_material, pdf_path)
        
        return {
            "success": True,
            "material_id": material_id,
            "topic": topic_name,
            "message": "Study material generated successfully",
            "content": study_material,
            "pdf": f"/api/study-materials/pdf/{pdf_filename}" if os.path.exists(pdf_path) else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        _log.error(f"Error generating study material: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/material/{material_id}")
async def get_study_material(
    material_id: str,
    current_user: dict = Depends(get_current_user_from_token)
) -> Dict[str, Any]:
    """Get previously generated study material"""
    try:
        if not db.database:
            raise HTTPException(status_code=500, detail="Database not available")
        
        from bson import ObjectId
        
        materials_collection = db.database["study_materials"]
        material = await materials_collection.find_one({
            "_id": ObjectId(material_id),
            "user_id": current_user.get("_id")
        })
        
        if not material:
            raise HTTPException(status_code=404, detail="Study material not found")
        
        # Convert ObjectId to string
        material["_id"] = str(material["_id"])
        material["user_id"] = str(material["user_id"])
        
        return {
            "success": True,
            "content": material
        }
        
    except HTTPException:
        raise
    except Exception as e:
        _log.error(f"Error retrieving study material: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback/{material_id}")
async def submit_feedback(
    material_id: str,
    feedback: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user_from_token)
) -> Dict[str, Any]:
    """Submit feedback and regenerate material at appropriate level"""
    try:
        if not db.database:
            raise HTTPException(status_code=500, detail="Database not available")
        
        from bson import ObjectId
        
        materials_collection = db.database["study_materials"]
        
        # Get existing material
        original_material = await materials_collection.find_one({
            "_id": ObjectId(material_id),
            "user_id": current_user.get("_id")
        })
        
        if not original_material:
            raise HTTPException(status_code=404, detail="Study material not found")
        
        _log.info(f"Received feedback for material {material_id}")
        
        # Analyze feedback and regenerate
        regenerated_material = await study_material_generator.analyze_feedback_and_regenerate(
            original_material,
            feedback
        )
        
        # Save regenerated material
        result = await materials_collection.update_one(
            {"_id": ObjectId(material_id)},
            {"$set": regenerated_material}
        )
        
        # Generate new PDF
        topic_id = original_material.get("topic_id", "unknown")
        pdf_filename = f"study_{topic_id}_{current_user.get('_id', 'user')}_v{regenerated_material.get('regeneration_count', 1)}.pdf"
        pdf_path = os.path.join(PDF_STORAGE_DIR, pdf_filename)
        background_tasks.add_task(pdf_generator.generate_pdf, regenerated_material, pdf_path)
        
        return {
            "success": True,
            "message": "Material regenerated based on feedback",
            "new_level": regenerated_material.get("learning_level"),
            "regeneration_count": regenerated_material.get("regeneration_count"),
            "content": regenerated_material,
            "pdf": f"/api/study-materials/pdf/{pdf_filename}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        _log.error(f"Error processing feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pdf/{filename}")
async def get_pdf(
    filename: str,
    current_user: dict = Depends(get_current_user_from_token)
):
    """Download generated PDF"""
    try:
        from fastapi.responses import FileResponse
        
        # Security check: ensure file is in correct directory
        pdf_path = os.path.join(PDF_STORAGE_DIR, filename)
        
        if not os.path.exists(pdf_path) or not pdf_path.startswith(PDF_STORAGE_DIR):
            raise HTTPException(status_code=404, detail="PDF not found")
        
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        _log.error(f"Error retrieving PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-all-topics")
async def generate_all_topics_materials(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user_from_token)
) -> Dict[str, Any]:
    """Generate study materials for ALL topics"""
    try:
        _log.info("Starting batch generation of study materials for all topics...")
        
        # Get all topics
        all_topics = []
        
        if db.database:
            try:
                topics_collection = db.database["topics"]
                cursor = topics_collection.find({})
                all_topics = await cursor.to_list(length=None)
            except:
                all_topics = []
        
        # If no topics found, return error
        if not all_topics:
            raise HTTPException(status_code=404, detail="No topics found in database")
        
        topic_count = len(all_topics)
        _log.info(f"Found {topic_count} topics to generate materials for")
        
        # Add background task to generate all materials
        background_tasks.add_task(
            _generate_materials_batch,
            all_topics,
            current_user.get("_id")
        )
        
        return {
            "success": True,
            "message": f"Batch generation started for {topic_count} topics",
            "topic_count": topic_count,
            "status": "processing"
        }
        
    except Exception as e:
        _log.error(f"Error initiating batch generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _generate_materials_batch(topics: list, user_id: str):
    """Background task to generate study materials for all topics"""
    try:
        for idx, topic in enumerate(topics, 1):
            try:
                topic_name = topic.get("topicName") or topic.get("name")
                _log.info(f"[{idx}/{len(topics)}] Generating material for: {topic_name}")
                
                study_material = await study_material_generator.generate_study_material(topic_name)
                
                if study_material and db.database:
                    materials_collection = db.database["study_materials"]
                    study_material["user_id"] = user_id
                    study_material["topic_id"] = str(topic.get("_id", topic_name))
                    
                    await materials_collection.insert_one(study_material)
                    _log.info(f"✅ Saved material for: {topic_name}")
                
                # Delay between requests
                await asyncio.sleep(1)
                
            except Exception as e:
                _log.error(f"Error generating material for topic: {e}")
                continue
        
        _log.info(f"✅ Batch generation completed for all {len(topics)} topics")
        
    except Exception as e:
        _log.error(f"Batch generation failed: {e}")


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
