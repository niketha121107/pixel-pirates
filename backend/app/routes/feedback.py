"""
User Feedback Routes — Save and retrieve per-topic feedback / ratings.
"""

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from typing import Optional
from app.models import SuccessResponse
from app.data import save_user_feedback, get_user_feedback
from app.core.auth import get_current_user_from_token

router = APIRouter()


class FeedbackIn(BaseModel):
    topic_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = ""


@router.post("", response_model=SuccessResponse)
async def submit_feedback(
    fb: FeedbackIn,
    current_user: dict = Depends(get_current_user_from_token),
):
    saved = save_user_feedback(current_user["id"], fb.topic_id, fb.rating, fb.comment)
    return SuccessResponse(success=True, message="Feedback submitted", data={"feedback": saved})


@router.get("", response_model=SuccessResponse)
async def list_feedback(
    topic_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user_from_token),
):
    fb_list = get_user_feedback(current_user["id"], topic_id)
    return SuccessResponse(success=True, message="Feedback retrieved", data={"feedback": fb_list})
