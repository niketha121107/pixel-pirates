"""
AI Chat Route — Provides conversational AI tutoring via Gemini
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional
from app.models import SuccessResponse
from app.services.adaptive_engine_service import adaptive_engine_service
from app.core.auth import get_current_user_from_token
import asyncio
import logging
import random

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatMessageIn(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessageIn]] = []
    language: Optional[str] = "en"


def _build_fallback_response(user_name: str, message: str, history: List[dict]) -> str:
    text = (message or '').strip()
    lower = text.lower()

    intro_options = [
        f"Hey {user_name}! 👋 Had a tiny connection hiccup, but no worries - I'm still here to help!",
        f"Hi {user_name}! 😊 My full AI brain took a coffee break, but I've got you covered with a focused answer!",
        f"Hello {user_name}! ✨ Quick mode activated! Let me break this down for you!",
    ]

    if 'for loop' in lower and 'python' in lower:
        body = (
            "Ooh, Python for loops! These are super useful! 🔄\n\n"
            "Think of a for loop like going through items in your backpack one by one:\n\n"
            "**How it works:**\n"
            "• It automatically grabs each item from a list/sequence\n"
            "• Runs your code for each item\n"
            "• Moves to the next one automatically\n\n"
            "**Example:**\n"
            "```python\n"
            "for i in range(5):\n"
            "    print(i)\n"
            "# Prints: 0, 1, 2, 3, 4\n"
            "```\n\n"
            "**Pro tip:** Need both index AND value? Use enumerate()!\n"
            "```python\n"
            "fruits = ['apple', 'banana']\n"
            "for index, fruit in enumerate(fruits):\n"
            "    print(f'{index}: {fruit}')\n"
            "```\n\n"
            "Want to see more examples? Just ask! 🚀"
        )
    elif 'while loop' in lower and 'python' in lower:
        body = (
            "Ah, while loops! The 'keep doing this until...' loop! 🔁\n\n"
            "**When to use it:**\n"
            "• When you don't know exactly how many times you'll loop\n"
            "• Perfect for 'keep trying until success' situations\n\n"
            "**Example:**\n"
            "```python\n"
            "count = 0\n"
            "while count < 3:\n"
            "    print(f'Count is {count}')\n"
            "    count += 1  # Don't forget this or it'll loop forever! ⚠️\n"
            "```\n\n"
            "**Important:** Always make sure your condition eventually becomes False, or you'll get stuck in an infinite loop! 😅\n\n"
            "Need help with a specific while loop scenario? Hit me up! 💪"
        )
    elif 'python' in lower:
        body = (
            "Python! Awesome choice! 🐍✨\n\n"
            "Here's your roadmap to Python mastery:\n\n"
            "**1. Basics (Start here!)** 🎯\n"
            "   • Variables and data types (numbers, strings, booleans)\n"
            "   • Input/output with print() and input()\n\n"
            "**2. Control Flow** 🔄\n"
            "   • if/elif/else conditions\n"
            "   • for and while loops\n\n"
            "**3. Data Structures** 📦\n"
            "   • Lists, dictionaries, sets, tuples\n"
            "   • When to use each one\n\n"
            "**4. Functions** ⚡\n"
            "   • def keyword, parameters, return values\n"
            "   • Making your code reusable!\n\n"
            "**5. Next Level** 🚀\n"
            "   • Classes and OOP\n"
            "   • File handling\n"
            "   • Error handling with try/except\n\n"
            "Which topic sounds interesting? I can break it down with examples! 😊"
        )
    elif 'javascript' in lower or 'js' in lower:
        body = (
            "JavaScript! The language that powers the web! 🌐✨\n\n"
            "**Your JS learning path:**\n\n"
            "**1. Fundamentals** 🎯\n"
            "   • Variables (let, const, var)\n"
            "   • Functions (regular and arrow functions)\n"
            "   • Arrays and objects\n\n"
            "**2. DOM Magic** 🎨\n"
            "   • Selecting elements\n"
            "   • Event listeners (clicks, hovers, etc.)\n"
            "   • Making pages interactive!\n\n"
            "**3. Async Superpowers** ⚡\n"
            "   • Promises and .then()\n"
            "   • async/await (the clean way!)\n"
            "   • Fetching data from APIs\n\n"
            "**4. Modern JS** 🚀\n"
            "   • Destructuring, spread operator\n"
            "   • Template literals\n"
            "   • Map, filter, reduce\n\n"
            "Pick a topic and I'll explain it like you're learning from a friend! What sounds good? 🤔"
        )
    else:
        body = (
            f"You asked: \"{text[:100]}{'...' if len(text) > 100 else ''}\"\n\n"
            "I want to give you the best answer! To help me understand what you need, try:\n\n"
            "**Format that works great:**\n"
            "• \"Explain [topic] to me like I'm a beginner\"\n"
            "• \"Show me code examples for [topic]\"\n"
            "• \"Give me practice questions on [topic]\"\n"
            "• \"What's the difference between [thing A] and [thing B]?\"\n\n"
            "**Example:**\n"
            "\"Explain Python for loops with 3 simple examples\" 👍\n\n"
            "Don't worry about getting it perfect - just ask naturally! I'm here to help! 😊"
        )

    last_assistant = ''
    for item in reversed(history or []):
        if item.get('role') == 'assistant':
            last_assistant = str(item.get('content') or '').strip()
            break

    response = f"{random.choice(intro_options)}\n\n{body}\n\n💡 **Pro tip:** I can also create custom quizzes, explain code you're stuck on, or help you debug! Just let me know what you need!"

    # Avoid sending identical fallback twice in a row.
    if last_assistant and response.strip() == last_assistant.strip():
        response += "\n\n🔍 **Bonus:** Paste your code and I'll review it line by line and help fix any issues!"

    return response


@router.post("/message", response_model=SuccessResponse)
async def send_chat_message(
    req: ChatRequest,
    current_user: dict = Depends(get_current_user_from_token),
):
    """Send a message to the AI tutor and receive a response"""
    try:
        user_name = current_user.get("name", "Student")

        # Build conversation history for context
        history = [
            {"role": m.role, "content": m.content}
            for m in (req.history or [])
        ]

        # Check if user is asking for an image/diagram
        lower_msg = req.message.lower()
        image_keywords = ["generate image", "show image", "draw", "diagram", "visualize", "illustration", "picture", "image to explain"]
        wants_image = any(kw in lower_msg for kw in image_keywords)

        image_data = None
        if wants_image:
            try:
                image_data = await asyncio.wait_for(
                    adaptive_engine_service.generate_image(req.message),
                    timeout=30.0,
                )
            except Exception as exc:
                logger.warning(f"Image generation failed: {exc}")

        try:
            ai_response = await asyncio.wait_for(
                adaptive_engine_service.chat(
                    message=req.message,
                    history=history,
                    user_name=user_name,
                    language=req.language or "en",
                ),
                timeout=35.0,
            )
        except asyncio.TimeoutError:
            logger.warning("AI chat timed out")
            ai_response = None
        except Exception as exc:
            logger.warning(f"AI chat error: {exc}")
            ai_response = None

        if not ai_response:
            ai_response = _build_fallback_response(
                user_name=user_name,
                message=req.message,
                history=history,
            )

        response_data: dict = {"response": ai_response}
        if image_data:
            response_data["image"] = image_data

        return SuccessResponse(
            success=True,
            message="Chat response generated",
            data=response_data,
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat message: {str(e)}",
        )
