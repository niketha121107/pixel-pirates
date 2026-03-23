"""
AI Chat Route — Provides conversational AI tutoring via Gemini
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional
from app.models import SuccessResponse
from app.services.adaptive_engine_service import adaptive_engine_service
from app.core.auth import get_current_user_from_token
from app.data import get_all_topics
import asyncio
import logging
import re

logger = logging.getLogger(__name__)

router = APIRouter()

OUT_OF_SCOPE_MESSAGE = "Sorry, I can only answer questions related to the provided learning topics."

INAPPROPRIATE_PATTERNS = [
    "how to kill", "how to hurt", "how to bomb", "how to hack", "how to cheat exam",
    "nude", "sex", "porn", "xxx", "adult content",
    "how to steal", "how to cheat", "how to commit fraud", "illegal",
    "racist", "sexist", "hate speech", "discriminate",
]

GENERIC_TOPIC_TERMS = {
    "programming", "coding", "algorithm", "algorithms", "data structure", "data structures",
    "array", "arrays", "string", "strings", "loop", "loops", "function", "functions",
    "class", "classes", "object", "objects", "recursion", "sorting", "searching",
    "complexity", "big o", "debug", "debugging", "python", "javascript", "java",
    "html", "css", "react", "fastapi", "database", "sql", "api"
}

STOP_WORDS = {
    "the", "a", "an", "and", "or", "for", "to", "of", "in", "on", "with", "by", "at",
    "is", "are", "be", "as", "it", "this", "that", "from", "about", "into", "using"
}


def _is_inappropriate_question(message: str) -> bool:
    """Check if the question contains inappropriate content"""
    msg_lower = message.lower().strip()
    for pattern in INAPPROPRIATE_PATTERNS:
        if pattern in msg_lower:
            return True
    return False


def _get_topic_terms() -> tuple[set[str], set[str]]:
    """Collect topic phrases and tokens from the configured learning topics."""
    phrases: set[str] = set()
    tokens: set[str] = set(GENERIC_TOPIC_TERMS)

    try:
        for topic in get_all_topics():
            name = str(topic.get("name") or topic.get("topicName") or "").strip().lower()
            language = str(topic.get("language") or "").strip().lower()

            if name:
                phrases.add(name)
                for piece in re.split(r"[^a-z0-9+#]+", name):
                    piece = piece.strip()
                    if len(piece) >= 3 and piece not in STOP_WORDS:
                        tokens.add(piece)

            if language and len(language) >= 3:
                tokens.add(language)
    except Exception as exc:
        logger.warning(f"Could not load topic terms for chat guard: {exc}")

    return phrases, tokens


def _is_topic_related(message: str) -> bool:
    """Allow only learning-topic questions based on configured topics and core study terms."""
    msg = (message or "").strip().lower()
    if not msg:
        return False

    phrases, tokens = _get_topic_terms()

    for phrase in phrases:
        if phrase and phrase in msg:
            return True

    message_tokens = {
        part.strip()
        for part in re.split(r"[^a-z0-9+#]+", msg)
        if part.strip() and part.strip() not in STOP_WORDS
    }

    if message_tokens & tokens:
        return True

    if any(term in msg for term in ("data structure", "big o", "time complexity", "space complexity")):
        return True

    return False


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

    if 'for loop' in lower and 'python' in lower:
        body = (
            "### Quick Answer\n"
            "A Python `for` loop iterates over each item in a sequence and executes a block for each item.\n\n"
            "### Key Points\n"
            "- Best when iterating known collections like lists, strings, and ranges.\n"
            "- Stops automatically when items are exhausted.\n"
            "- Reduces manual index handling compared to `while`.\n\n"
            "### Example\n"
            "```python\n"
            "for i in range(5):\n"
            "    print(i)\n"
            "# Prints: 0, 1, 2, 3, 4\n"
            "```\n"
            "`range(5)` generates values 0 through 4, and each value is assigned to `i` for one iteration.\n\n"
            "### Next Step\n"
            "Try using `enumerate()` to get both index and value in the same loop."
        )
    elif 'while loop' in lower and 'python' in lower:
        body = (
            "### Quick Answer\n"
            "A Python `while` loop repeats as long as its condition remains `True`.\n\n"
            "### Key Points\n"
            "- Useful when iteration count is unknown in advance.\n"
            "- Condition is checked before each iteration.\n"
            "- Update loop variables to avoid infinite loops.\n\n"
            "### Example\n"
            "```python\n"
            "count = 0\n"
            "while count < 3:\n"
            "    print(f'Count is {count}')\n"
            "    count += 1\n"
            "```\n"
            "The update `count += 1` guarantees the condition eventually becomes false.\n\n"
            "### Next Step\n"
            "Practice with a `while` loop that reads input until the user types `quit`."
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
            "Study in this order: variables -> conditions -> loops -> functions, then build one mini project."
        )
    elif 'javascript' in lower or 'js' in lower:
        body = (
            "### Quick Answer\n"
            "JavaScript is the core language for interactive web applications.\n\n"
            "### Key Points\n"
            "- Start with variables, functions, arrays, and objects.\n"
            "- Learn DOM manipulation and event handling for browser apps.\n"
            "- Use `async/await` for API calls and asynchronous logic.\n"
            "- Modern syntax like destructuring and spread improves readability.\n\n"
            "### Example\n"
            "```javascript\n"
            "const names = ['Ana', 'Sam'];\n"
            "const upper = names.map((n) => n.toUpperCase());\n"
            "console.log(upper);\n"
            "```\n"
            "This example transforms an array using `map`, a core JavaScript pattern.\n\n"
            "### Next Step\n"
            "Build a small page that fetches and displays API data using `fetch` and `async/await`."
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

    return body


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

        if _is_inappropriate_question(req.message) or not _is_topic_related(req.message):
            return SuccessResponse(
                success=True,
                message="Chat response generated",
                data={"response": OUT_OF_SCOPE_MESSAGE},
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
