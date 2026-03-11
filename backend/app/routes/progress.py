"""
User Progress Routes — Detailed per-topic progress with time tracking and mock test results.
"""

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.models import SuccessResponse
from app.data import (
    save_topic_progress,
    get_topic_progress,
    save_mock_result,
    get_mock_results,
)
from app.core.auth import get_current_user_from_token

router = APIRouter()


class TopicProgressIn(BaseModel):
    topic_id: str
    time_spent: int = 0  # seconds
    quiz_score: Optional[int] = None
    quiz_total: Optional[int] = None
    attempts: int = 1
    status: str = "in-progress"


class MockResultIn(BaseModel):
    topics: list
    score: int
    total_questions: int
    percentage: float
    time_taken: int = 0  # seconds
    answers: Optional[list] = []


@router.post("/topic", response_model=SuccessResponse)
async def upsert_topic_progress(
    prog: TopicProgressIn,
    current_user: dict = Depends(get_current_user_from_token),
):
    saved = save_topic_progress(current_user["id"], prog.topic_id, prog.dict(exclude={"topic_id"}))
    return SuccessResponse(success=True, message="Progress saved", data={"progress": saved})


@router.get("/topic", response_model=SuccessResponse)
async def list_topic_progress(
    topic_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user_from_token),
):
    records = get_topic_progress(current_user["id"], topic_id)
    return SuccessResponse(success=True, message="Progress retrieved", data={"progress": records})


@router.post("/mock-result", response_model=SuccessResponse)
async def save_mock_test_result(
    result: MockResultIn,
    current_user: dict = Depends(get_current_user_from_token),
):
    saved = save_mock_result(current_user["id"], result.dict())
    return SuccessResponse(success=True, message="Mock test result saved", data={"result": saved})


@router.get("/mock-results", response_model=SuccessResponse)
async def list_mock_test_results(
    current_user: dict = Depends(get_current_user_from_token),
):
    results = get_mock_results(current_user["id"])
    return SuccessResponse(success=True, message="Mock results retrieved", data={"results": results})
