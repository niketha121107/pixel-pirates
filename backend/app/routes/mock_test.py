"""
Mock Test API Routes
Handles question generation, rules, and violation tracking
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import logging
from app.core.auth import get_current_user_from_token
from app.services.mock_test_service import mock_test_service, ViolationType

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/mock-test", tags=["Mock Test"])

class ViolationRequest(BaseModel):
    violation_type: str

@router.get("/rules")
async def get_mock_test_rules() -> Dict[str, Any]:
    """Get rules for mock test"""
    try:
        rules = await mock_test_service.get_mock_test_rules()
        return {
            "success": True,
            "rules": rules
        }
    except Exception as e:
        logger.error(f"Error getting rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-questions/{topic_name}")
async def generate_mock_questions(
    topic_name: str,
    num_questions: int = 10,
    current_user: dict = Depends(get_current_user_from_token)
) -> Dict[str, Any]:
    """Generate mock test questions for a topic using Gemini 2.5 Flash"""
    
    try:
        # Check if user is suspended
        suspension_status = await mock_test_service.check_suspension_status(
            str(current_user.get("_id"))
        )
        
        if suspension_status["is_suspended"]:
            raise HTTPException(
                status_code=403,
                detail=f"Your account is suspended until {suspension_status['suspension_until']}. You violated mock test rules too many times."
            )
        
        logger.info(f"Generating {num_questions} questions for topic: {topic_name}")
        
        questions = await mock_test_service.generate_mock_test_questions(
            topic_name, 
            num_questions
        )
        
        return {
            "success": True,
            "topic": topic_name,
            "total_questions": len(questions),
            "questions": questions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating questions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/record-violation")
async def record_violation(
    request: ViolationRequest,
    current_user: dict = Depends(get_current_user_from_token)
) -> Dict[str, Any]:
    """Record a mock test violation (screenshot, copy, tab switch)"""
    
    try:
        user_id = str(current_user.get("_id"))
        violation_type = request.violation_type
        
        # Map violation type
        try:
            v_type = ViolationType(violation_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid violation type: {violation_type}")
        
        violation_result = await mock_test_service.record_violation(user_id, v_type)
        
        logger.warning(
            f"⚠️ VIOLATION RECORDED - User: {user_id}, Type: {violation_type}, "
            f"Count: {violation_result['violation_count']}"
        )
        
        return {
            "success": True,
            "violation_type": violation_type,
            "violation_count": violation_result["violation_count"],
            "warning_number": violation_result["warning_number"],
            "is_suspended": violation_result["is_suspended"],
            "suspension_until": violation_result["suspension_until"],
            "message": get_violation_message(violation_result["warning_number"], violation_result["is_suspended"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording violation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/suspension-status")
async def check_suspension(
    current_user: dict = Depends(get_current_user_from_token)
) -> Dict[str, Any]:
    """Check if user is suspended from mock tests"""
    
    try:
        user_id = str(current_user.get("_id"))
        status = await mock_test_service.check_suspension_status(user_id)
        
        return {
            "success": True,
            "is_suspended": status["is_suspended"],
            "violations": status["violations"],
            "suspension_until": status.get("suspension_until"),
            "suspension_lifted": status.get("suspension_lifted", False)
        }
        
    except Exception as e:
        logger.error(f"Error checking suspension: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def get_violation_message(warning_number: int, is_suspended: bool) -> str:
    """Get appropriate message for violation"""
    
    if is_suspended:
        return f"🚫 ACCOUNT SUSPENDED: You have exceeded the maximum allowed violations (10). Your account has been suspended for 6 hours. Please try again later."
    
    if warning_number >= 10:
        return f"⚠️ CRITICAL WARNING {warning_number}/10: This is your final warning! One more violation will result in a 6-hour account suspension!"
    
    if warning_number >= 8:
        return f"⚠️ SERIOUS WARNING {warning_number}/10: You are close to suspension. {11 - warning_number - 1} violations remaining before suspension."
    
    if warning_number >= 5:
        return f"⚠️ WARNING {warning_number}/10: Be careful. {11 - warning_number} violations until suspension."
    
    if warning_number == 1:
        return f"⚠️ First violation recorded. Please follow the mock test rules to avoid suspension."
    
    return f"⚠️ Violation {warning_number} recorded."
