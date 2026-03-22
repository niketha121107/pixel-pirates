from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Dict, Any, Optional
from app.models import Topic, TopicProgress, TopicStatus, SuccessResponse
from app.data import get_all_topics, get_topic_by_id, get_user_by_id, update_user_topic_progress
from app.core.auth import get_current_user_from_token
from app.visual_formatter import get_visual_explanation_with_fallback

router = APIRouter()

@router.get("", response_model=SuccessResponse)
async def get_topics(
    language: Optional[str] = Query(None, description="Filter by programming language"),
    status: Optional[str] = Query(None, description="Filter by completion status"),
    search: Optional[str] = Query(None, description="Search topics by title"),
    current_user: dict = Depends(get_current_user_from_token)
):
    """Get all topics with user's progress status"""
    topics = get_all_topics()
    user = current_user
    
    # Add user progress to each topic
    quiz_scores = user.get("quizScores", {})
    topics_with_progress = []
    for topic in topics:
        topic_id = topic.get("id") or str(topic.get("_id", ""))
        topic_name = topic.get("name", "")
        
        topic_data = {
            "id": topic_id,
            "topicName": topic_name,  # Map 'name' to 'topicName'
            "name": topic_name,  # Keep both for compatibility
            "language": topic.get("language", ""),
            "difficulty": topic.get("difficulty", ""),
            "overview": topic.get("overview", ""),
        }
        
        # Determine status for this user
        if topic_id in user.get("completedTopics", []):
            topic_data["status"] = "completed"
            topic_data["score"] = quiz_scores.get(topic_id, 0)
            topic_data["total"] = 100
        elif topic_id in user.get("inProgressTopics", []):
            topic_data["status"] = "in-progress"
            topic_data["score"] = 0
            topic_data["total"] = 100
        else:
            topic_data["status"] = "pending"
            topic_data["score"] = 0
            topic_data["total"] = 100
        
        # Apply filters
        if language and topic["language"].lower() != language.lower():
            continue
        if status and topic_data["status"] != status:
            continue
        if search and search.lower() not in topic_name.lower():
            continue
            
        topics_with_progress.append(topic_data)
    
    return SuccessResponse(
        success=True,
        message="Topics retrieved successfully",
        data={"topics": topics_with_progress}
    )

@router.get("/{topic_id}", response_model=SuccessResponse)
async def get_topic_details(
    topic_id: str,
    current_user: dict = Depends(get_current_user_from_token)
):
    """Get detailed information about a specific topic, with live YouTube videos."""
    topic = get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Topic not found"
        )
    
    user = current_user
    
    # Transform MongoDB document to frontend format
    topic_data = {
        "id": topic.get("id") or str(topic.get("_id", "")),
        "topicName": topic.get("name", ""),  # Map 'name' to 'topicName'
        "language": topic.get("language", ""),
        "difficulty": topic.get("difficulty", ""),
        "overview": topic.get("overview", ""),
        "status": "pending",
        "userScore": 0,
    }
    
    # Add user's progress status
    quiz_scores = user.get("quizScores", {})
    if topic_id in user.get("completedTopics", []):
        topic_data["status"] = "completed"
        topic_data["userScore"] = quiz_scores.get(topic_id, 0)
    elif topic_id in user.get("inProgressTopics", []):
        topic_data["status"] = "in-progress"
    
    # --- Transform explanations from dict to array format with fallback ---
    explanations_dict = topic.get("explanations", {})
    explanations_array = []
    
    # Check if visual explanation needs fallback
    visual_content = explanations_dict.get("visual", "")
    if not visual_content or len(str(visual_content).strip()) < 100:
        # Generate visual from other explanations
        visual_content = get_visual_explanation_with_fallback(topic)
    
    if isinstance(explanations_dict, dict):
        for style, content in explanations_dict.items():
            # Use fallback visual if this is the visual style and it's empty
            if style == "visual" and (not visual_content or len(str(visual_content).strip()) < 100):
                content = visual_content
            
            if isinstance(content, dict):
                explanations_array.append({
                    "style": style,
                    "title": content.get("title", f"{style.capitalize()} Explanation"),
                    "content": content.get("content", ""),
                    "codeExample": content.get("codeExample", ""),
                })
            elif isinstance(content, str):
                explanations_array.append({
                    "style": style,
                    "title": f"{style.capitalize()} Explanation",
                    "content": content,
                    "codeExample": "",
                })
    
    # Ensure visual explanation is always present and substantial
    visual_found = any(e["style"] == "visual" for e in explanations_array)
    if not visual_found and visual_content:
        explanations_array.append({
            "style": "visual",
            "title": "Visual Explanation",
            "content": visual_content,
            "codeExample": "",
        })
    
    topic_data["explanations"] = explanations_array
    
    # --- Transform videos to have youtubeId field ---
    videos = topic.get("videos", [])
    recommended_videos = []
    for video in videos:
        if isinstance(video, dict):
            recommended_videos.append({
                "youtubeId": video.get("youtubeId") or video.get("videoId", ""),
                "title": video.get("title", ""),
                "channel": video.get("channel", ""),
                "views": video.get("views", 0),
                "uploadedAt": video.get("uploadedAt", ""),
                "url": video.get("url", ""),
                "description": video.get("description", ""),
            })
    topic_data["recommendedVideos"] = recommended_videos
    
    # --- Add comprehensive study material ---
    # Priority: use study_material if available, fall back to key_notes
    study_material_obj = topic.get("study_material")
    key_notes = topic.get("key_notes", "")
    
    if study_material_obj and isinstance(study_material_obj, dict):
        # Use comprehensive study material with all sections
        # Transform domain_usage into implementation array
        domain_usage = study_material_obj.get("domain_usage", "")
        implementation = []
        if domain_usage:
            # Split by newlines or bullets to create implementation array
            for line in domain_usage.split('\n'):
                line = line.strip()
                if line and line not in ['', '-', '•', '*']:
                    # Remove leading bullet points if any
                    line = line.lstrip('- •*').strip()
                    if line:
                        implementation.append(line)
        
        topic_data["studyMaterial"] = {
            "title": topic.get("name", ""),
            "overview": study_material_obj.get("overview", ""),
            "explanation": study_material_obj.get("explanation", ""),
            "syntax": study_material_obj.get("syntax", ""),
            "codeExample": study_material_obj.get("example", ""),  # Map example to codeExample
            "implementation": implementation,  # Convert domain_usage to implementation array
            "advantages": study_material_obj.get("advantages", "").split('\n') if study_material_obj.get("advantages", "") else [],
            "disadvantages": study_material_obj.get("disadvantages", "").split('\n') if study_material_obj.get("disadvantages", "") else [],
            "keyPoints": [],  # Can be populated if needed
            "type": "comprehensive"
        }
    elif key_notes:
        # Fallback to key_notes
        topic_data["studyMaterial"] = {
            "title": topic.get("name", ""),
            "overview": key_notes,
            "type": "key_notes"
        }
    else:
        topic_data["studyMaterial"] = {}

    # --- Prioritize stored database videos first ---
    stored_video_count = len(topic_data.get("recommendedVideos", []))
    
    if stored_video_count > 0:
        # Already have stored videos - use them
        print(f"✅ Using {stored_video_count} stored videos for: {topic_data['topicName']}")
    else:
        # No stored videos - try to fetch fresh YouTube videos as fallback
        import asyncio, logging
        _log = logging.getLogger(__name__)
        try:
            from app.services.youtube_service import youtube_service
            print(f"🎬 No stored videos found. Fetching YouTube videos for: {topic_data['topicName']}")
            live_videos = await asyncio.wait_for(
                youtube_service.search_for_topic(
                    topic_name=topic_data["topicName"],
                    language=topic_data.get("language", ""),
                    max_results=3,
                ),
                timeout=5.0,
            )
            if live_videos:
                print(f"✅ Successfully fetched {len(live_videos)} fresh YouTube videos")
                topic_data["recommendedVideos"] = live_videos
                _log.info(f"Fetched {len(live_videos)} fresh YouTube videos for {topic_data['topicName']}")
            else:
                print(f"⚠️ YouTube API returned no results for: {topic_data['topicName']}")
        except asyncio.TimeoutError as te:
            print(f"⏱️ YouTube API timeout for {topic_data['topicName']}")
            _log.warning(f"YouTube API timeout — no videos available for {topic_data['topicName']}")
        except Exception as e:
            print(f"⚠️ YouTube API error (expected): {str(e)[:100]}")
            _log.warning(f"YouTube API error for {topic_data['topicName']} — no fresh videos available")

    return SuccessResponse(
        success=True,
        message="Topic details retrieved successfully",
        data={"topic": topic_data}
    )

@router.put("/{topic_id}/status", response_model=SuccessResponse)
async def update_topic_status(
    topic_id: str,
    progress: TopicProgress,
    current_user: dict = Depends(get_current_user_from_token)
):
    """Update user's progress status for a topic"""
    topic = get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Topic not found"
        )
    
    success = update_user_topic_progress(
        current_user["id"], 
        topic_id, 
        progress.status.value,
        progress.score
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return SuccessResponse(
        success=True,
        message=f"Topic status updated to {progress.status}",
        data={
            "topicId": topic_id,
            "status": progress.status.value,
            "score": progress.score
        }
    )

@router.get("/{topic_id}/fresh-videos", response_model=SuccessResponse)
async def get_fresh_videos(
    topic_id: str,
    max_results: int = Query(3, description="Maximum number of videos to return"),
    current_user: dict = Depends(get_current_user_from_token)
):
    """Fetch fresh YouTube videos for a topic on-demand (requires billing enabled)"""
    import asyncio
    import logging
    
    topic = get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )
    
    _log = logging.getLogger(__name__)
    
    try:
        from app.services.youtube_service import youtube_service
        
        print(f"🎬 Fetching fresh YouTube videos for: {topic['name']}")
        
        # Fetch fresh videos from YouTube with timeout
        fresh_videos = await asyncio.wait_for(
            youtube_service.search_for_topic(
                topic_name=topic.get("name", ""),
                language=topic.get("language", ""),
                max_results=max_results,
            ),
            timeout=10.0,  # Longer timeout for on-demand requests
        )
        
        if fresh_videos:
            print(f"✅ Successfully fetched {len(fresh_videos)} fresh YouTube videos")
            _log.info(f"Fresh videos fetched for {topic_id} by user {current_user['id']}: {len(fresh_videos)} results")
            
            return SuccessResponse(
                success=True,
                message=f"Fresh videos fetched successfully",
                data={
                    "topicId": topic_id,
                    "recommendedVideos": fresh_videos,
                    "source": "youtube_fresh",
                    "count": len(fresh_videos)
                }
            )
        else:
            return SuccessResponse(
                success=False,
                message="YouTube API returned no results",
                data={
                    "topicId": topic_id,
                    "recommendedVideos": [],
                    "source": "youtube_fresh",
                    "count": 0
                }
            )
            
    except asyncio.TimeoutError:
        _log.warning(f"YouTube API timeout for {topic_id}")
        raise HTTPException(
            status_code=504,
            detail="YouTube API request timed out. Please ensure billing is enabled on Google Cloud."
        )
    except Exception as e:
        error_msg = str(e)
        _log.error(f"YouTube API error for {topic_id}: {error_msg}")
        
        # Check if it's a quota error
        if "quotaExceeded" in error_msg or "quota" in error_msg.lower():
            raise HTTPException(
                status_code=429,
                detail="YouTube API quota exceeded. Please enable billing on Google Cloud Console."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch fresh videos: {error_msg[:100]}"
            )

@router.get("/{topic_id}/explanation", response_model=SuccessResponse)
async def get_personalized_explanation(
    topic_id: str,
    style: Optional[str] = Query(None, description="Explanation style: visual, simplified, logical, analogy"),
    language: Optional[str] = Query("en", description="Language code: en, hi, es, fr, de, etc."),
    current_user: dict = Depends(get_current_user_from_token)
):
    """Get AI-generated personalized explanation for a topic"""
    topic = get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Topic not found"
        )
    
    user = current_user
    
    # Use user's preferred style if not specified
    explanation_style = style or user.get("preferredStyle", "visual")
    
    try:
        from app.services.adaptive_engine_service import adaptive_engine_service
        
        # Generate personalized explanation using Gemini AI
        ai_explanation = await adaptive_engine_service.get_personalized_explanation(
            topic=topic["topicName"],
            user_preferred_style=explanation_style,
            difficulty_level=topic["difficulty"],
            additional_context=topic["overview"],
            language=language or "en"
        )
        
        # Also include existing explanations
        existing_explanations = topic.get("explanations", [])
        
        return SuccessResponse(
            success=True,
            message="Personalized explanation generated",
            data={
                "topicId": topic_id,
                "topicName": topic["topicName"],
                "aiExplanation": {
                    "style": explanation_style,
                    "content": ai_explanation,
                    "generated": True
                },
                "existingExplanations": existing_explanations
            }
        )
        
    except Exception as e:
        # Fallback to existing explanations
        existing_explanations = topic.get("explanations", [])
        preferred_explanation = next(
            (exp for exp in existing_explanations if exp["style"] == explanation_style),
            existing_explanations[0] if existing_explanations else None
        )
        
        return SuccessResponse(
            success=True,
            message="Existing explanation retrieved",
            data={
                "topicId": topic_id,
                "topicName": topic["topicName"],
                "explanation": preferred_explanation,
                "existingExplanations": existing_explanations
            }
        )

@router.get("/{topic_id}/quiz", response_model=SuccessResponse)
async def get_topic_quiz(
    topic_id: str,
    subtopicId: Optional[str] = Query(None, description="Optional subtopic ID to get subtopic-specific quiz"),
    current_user: dict = Depends(get_current_user_from_token)
):
    """Get quiz questions for a specific topic or subtopic"""
    topic = get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    topic_name = topic.get("topicName") or topic.get("name", "Programming Concept")
    quiz_name = topic_name
    
    # Try to get stored quiz first
    quiz = topic.get("quiz", [])
    
    if subtopicId:
        for sub in topic.get("subtopics", []):
            if sub.get("id") == subtopicId:
                quiz = sub.get("quiz", quiz)
                quiz_name = sub.get("name", topic_name)
                break
    
    # If no stored quiz or it's empty, generate using AI
    if not quiz or len(quiz) == 0:
        try:
            from app.services.ai_content_service import ai_generator
            import logging
            _log = logging.getLogger(__name__)
            _log.info(f"No stored quiz found. Generating AI quiz for {topic_name}")
            
            # Generate fresh AI questions
            questions = await ai_generator.generate_quiz_questions(
                topic_name=topic_name,
                num_questions=5,
                difficulty=topic.get("difficulty", "mixed")
            )
            
            if questions:
                quiz = questions
                _log.info(f"Generated {len(questions)} AI questions for {topic_name}")
        except Exception as e:
            import logging
            _log = logging.getLogger(__name__)
            _log.warning(f"Failed to generate AI quiz for {topic_name}: {e}")
            # Fall through with empty quiz, which will be handled below
    
    # Return whatever we have (stored, AI-generated, or empty)
    return SuccessResponse(
        success=True,
        message="Quiz questions retrieved successfully",
        data={
            "topicId": topic_id,
            "topicName": quiz_name,
            "quiz": quiz
        }
    )