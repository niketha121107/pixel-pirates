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
import re

logger = logging.getLogger(__name__)

router = APIRouter()

# Keywords/patterns that indicate inappropriate content
INAPPROPRIATE_PATTERNS = [
    # Violence/harm
    'how to kill', 'how to hurt', 'how to bomb', 'how to hack', 'how to cheat exam',
    # Explicit content
    'nude', 'sex', 'porn', 'xxx', 'adult content',
    # Illegal activities
    'how to steal', 'how to cheat', 'how to commit fraud', 'illegal',
    # Hate/discrimination
    'racist', 'sexist', 'hate speech', 'discriminate',
]


def _is_inappropriate_question(message: str) -> bool:
    """Check if the question contains inappropriate content"""
    msg_lower = message.lower().strip()
    for pattern in INAPPROPRIATE_PATTERNS:
        if pattern in msg_lower:
            return True
    return False


def _build_redirect_response(user_name: str) -> str:
    """Build a friendly redirect message for inappropriate questions"""
    responses = [
        f"Hey {user_name}! 👋 I appreciate your curiosity, but that's not something I can help with here. "
        f"Remember, we're here on this platform to learn and grow together! 📚✨ "
        f"How about we focus on something related to your learning goals instead? "
        f"I'd love to help you master programming, data structures, algorithms, or any other tech topic! What would you like to learn? 🚀",
        
        f"Hi {user_name}! 😊 I'm here specifically to support your learning journey on this platform. "
        f"That question isn't related to your studies, so let's keep our chat focused on helping you succeed! 💪 "
        f"Whether it's Python, JavaScript, Java, or other programming topics, I'm ready to help! What shall we learn today? 📖",
        
        f"Hello {user_name}! 👨‍💻 This platform is all about building your tech skills and knowledge! "
        f"That topic doesn't fit our learning mission, so let's redirect to something constructive. "
        f"I can help you understand complex concepts, debug code, create quizzes, or explore new topics in tech! What interests you? 🎯",
    ]
    return random.choice(responses)


def _strip_followup_greeting(text: str, user_name: str) -> str:
    """Remove greeting-style opener for non-first messages.

    This keeps the first message friendly, but follow-ups direct.
    """
    if not text:
        return text

    normalized_name = re.escape((user_name or "").strip())
    first_line, *rest = text.split("\n")
    first = first_line.strip()

    patterns = [
        rf"^(hey|hi|hello|hiya|greetings)\b",
        rf"^(hey|hi|hello)\s+{normalized_name}\b",
    ]

    if any(re.search(p, first, flags=re.IGNORECASE) for p in patterns):
        cleaned_first = re.sub(
            rf"^(hey|hi|hello|hiya|greetings)(\s+{normalized_name})?\s*[,!\-:\.]?\s*",
            "",
            first,
            flags=re.IGNORECASE,
        ).strip()
        rebuilt = [cleaned_first] if cleaned_first else []
        rebuilt.extend(rest)
        return "\n".join(rebuilt).strip()

    return text


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
            "### Quick Answer\n"
            "Python is beginner-friendly, powerful, and used in web, AI, automation, and data work.\n\n"
            "### Key Points\n"
            "- Clean syntax that is easy to read and write\n"
            "- Huge ecosystem of libraries for real projects\n"
            "- Great for both beginners and advanced developers\n"
            "- Works for scripting, backend, data science, and ML\n\n"
            "### Example\n"
            "```python\n"
            "name = 'test3'\n"
            "print(f'Hello, {name}!')\n"
            "```\n"
            "This prints a personalized greeting and shows how readable Python is.\n\n"
            "### Next Step\n"
            "Want a quick mini-path: variables -> conditions -> loops -> functions?"
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
            "### Quick Answer\n"
            f"I can definitely help with: \"{text[:100]}{'...' if len(text) > 100 else ''}\".\n\n"
            "### Key Points\n"
            "- Tell me the exact topic or concept\n"
            "- Mention your level: beginner / intermediate / advanced\n"
            "- Say whether you want theory, code, or practice questions\n\n"
            "### Example Prompt\n"
            "- \"Explain Python for loops like I'm a beginner with 2 examples.\"\n"
            "- \"Compare list vs tuple with one code sample.\"\n\n"
            "### Next Step\n"
            "Share your exact learning goal and I’ll structure a crisp answer for you."
        )

    last_assistant = ''
    for item in reversed(history or []):
        if item.get('role') == 'assistant':
            last_assistant = str(item.get('content') or '').strip()
            break

    has_history = bool(history and len(history) > 0)
    if has_history:
        response = f"{body}\n\n💡 **Pro tip:** I can also create custom quizzes, explain code you're stuck on, or help you debug! Just let me know what you need!"
    else:
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

        # Check if the question is inappropriate (redirect instead of refusing)
        if _is_inappropriate_question(req.message):
            ai_response = _build_redirect_response(user_name)
            return SuccessResponse(
                success=True,
                message="Chat response generated",
                data={"response": ai_response},
            )

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

        # Keep follow-up replies direct: no repeated greetings after first turn.
        if history and len(history) > 0:
            ai_response = _strip_followup_greeting(ai_response, user_name)

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
