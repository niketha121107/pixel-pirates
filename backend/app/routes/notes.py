"""
User Notes Routes — Save and retrieve study notes per topic.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional
from app.models import SuccessResponse
from app.data import save_user_note, get_user_notes, delete_user_note
from app.core.auth import get_current_user_from_token

router = APIRouter()


class NoteIn(BaseModel):
    topic_id: str
    title: Optional[str] = ""
    content: str


@router.post("", response_model=SuccessResponse)
async def create_or_update_note(
    note: NoteIn,
    current_user: dict = Depends(get_current_user_from_token),
):
    saved = save_user_note(current_user["id"], note.topic_id, note.content, note.title)
    return SuccessResponse(success=True, message="Note saved", data={"note": saved})


@router.get("", response_model=SuccessResponse)
async def list_notes(
    topic_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user_from_token),
):
    notes = get_user_notes(current_user["id"], topic_id)
    return SuccessResponse(success=True, message="Notes retrieved", data={"notes": notes})


@router.delete("/{topic_id}", response_model=SuccessResponse)
async def remove_note(
    topic_id: str,
    current_user: dict = Depends(get_current_user_from_token),
):
    ok = delete_user_note(current_user["id"], topic_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return SuccessResponse(success=True, message="Note deleted")
