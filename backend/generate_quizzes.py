"""
Generate real quiz questions for all topics using Gemini AI.
Each topic gets 5 unique, content-relevant MCQ questions.

Usage:
    python generate_quizzes.py
"""

import os, sys, time, json, re, logging
from dotenv import load_dotenv
from pymongo import MongoClient
import httpx

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
MONGO_DB = os.getenv("MONGODB_DATABASE", "pixel_pirates")

GEMINI_MODELS = [
    "gemini-flash-latest",
    "gemini-3-flash-preview",
    "gemini-3.1-flash-lite-preview",
    "gemma-3-27b-it",
    "gemma-3-12b-it",
    "gemma-3-4b-it",
]

GEMINI_DELAY = 8  # seconds between requests

client = MongoClient(MONGO_URL)
db = client[MONGO_DB]

exhausted_models = set()


def call_gemini(prompt: str, retries: int = 12) -> str:
    """Call Gemini API with model rotation and retry logic."""
    available = [m for m in GEMINI_MODELS if m not in exhausted_models]
    if not available:
        log.warning("All models exhausted, waiting 90s...")
        time.sleep(90)
        exhausted_models.clear()
        available = list(GEMINI_MODELS)

    for attempt in range(retries):
        model = available[attempt % len(available)]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            resp = httpx.post(url, json=payload, timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return text
            elif resp.status_code == 429:
                log.warning(f"  429 from {model}, trying next...")
                exhausted_models.add(model)
                available = [m for m in GEMINI_MODELS if m not in exhausted_models]
                if not available:
                    log.warning("  All models exhausted, waiting 90s...")
                    time.sleep(90)
                    exhausted_models.clear()
                    available = list(GEMINI_MODELS)
                continue
            else:
                log.warning(f"  {resp.status_code} from {model}: {resp.text[:100]}")
                time.sleep(3)
        except Exception as e:
            log.warning(f"  Error with {model}: {e}")
            time.sleep(3)

    return ""


def generate_quiz_for_topic(topic: dict) -> list:
    """Generate 5 unique MCQ quiz questions for a topic."""
    topic_name = topic["topicName"]
    language = topic["language"]
    overview = topic.get("overview", "")
    difficulty = topic.get("difficulty", "Intermediate")

    # Get subtopic names for better context
    subtopics = [s.get("name", "") for s in topic.get("subtopics", [])]
    subtopic_str = ", ".join(subtopics[:5]) if subtopics else "general concepts"

    prompt = f"""Generate exactly 5 multiple-choice quiz questions about "{topic_name}" in {language} programming.

Topic overview: {overview[:500]}
Subtopics covered: {subtopic_str}
Difficulty: {difficulty}

Requirements:
- Each question must be UNIQUE and different from others
- Questions should test real knowledge about {topic_name} in {language}
- Each question has exactly 4 options (A, B, C, D)
- Only ONE option is correct
- Include a brief explanation for the correct answer
- Questions should be practical and educational

Return ONLY a valid JSON array with exactly 5 objects. No markdown, no code fences, just the JSON array.
Each object must have:
- "question": the question text (string)
- "options": array of exactly 4 option strings
- "correctAnswer": index of the correct option (0, 1, 2, or 3)
- "explanation": brief explanation of why the answer is correct (string)

Example format:
[
  {{
    "question": "What does the len() function return in Python?",
    "options": ["The type of object", "The length/size of an object", "A boolean value", "The memory address"],
    "correctAnswer": 1,
    "explanation": "len() returns the number of items in a container or the length of a string."
  }}
]"""

    text = call_gemini(prompt)
    if not text:
        return []

    # Extract JSON from response
    text = text.strip()
    # Remove markdown code fences if present
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    text = text.strip()

    try:
        questions = json.loads(text)
        if not isinstance(questions, list):
            return []

        # Validate and format questions
        formatted = []
        for i, q in enumerate(questions[:5]):
            if not isinstance(q, dict):
                continue
            question_text = q.get("question", "")
            options = q.get("options", [])
            correct = q.get("correctAnswer", 0)
            explanation = q.get("explanation", "Review this concept for deeper understanding.")

            if not question_text or len(options) != 4:
                continue
            if not isinstance(correct, int) or correct < 0 or correct > 3:
                correct = 0

            formatted.append({
                "id": f"q-{topic['id'].split('-')[1]}-{i+1}",
                "question": question_text,
                "options": options,
                "correctAnswer": correct,
                "explanation": explanation,
                "type": "mcq",
            })

        return formatted
    except json.JSONDecodeError:
        log.warning(f"  Failed to parse JSON for {topic_name}")
        return []


def main():
    topics = list(db.topics.find({}).sort("id", 1))
    log.info(f"Found {len(topics)} topics")

    success = 0
    failed = 0

    for i, topic in enumerate(topics):
        topic_name = topic["topicName"]
        language = topic["language"]
        topic_id = topic["id"]

        # Check if already has real questions (not placeholder)
        existing = topic.get("quiz", [])
        has_real = False
        if existing and len(existing) >= 5:
            # Check if questions are NOT placeholder
            first_q = existing[0].get("question", "")
            if "Option A" not in first_q and "Option B" not in str(existing[0].get("options", [])):
                # Check if questions are not all identical
                questions_set = set(q.get("question", "") for q in existing[:5])
                if len(questions_set) >= 3:  # At least 3 unique questions
                    has_real = True

        if has_real:
            log.info(f"[{i+1}/{len(topics)}] {topic_id} {topic_name} ({language}) — already has real questions, skipping")
            success += 1
            continue

        log.info(f"[{i+1}/{len(topics)}] Generating quiz for {topic_id}: {topic_name} ({language})...")
        questions = generate_quiz_for_topic(topic)

        if questions and len(questions) >= 3:
            db.topics.update_one(
                {"id": topic_id},
                {"$set": {"quiz": questions}}
            )
            log.info(f"  ✓ Generated {len(questions)} questions")
            success += 1
        else:
            log.warning(f"  ✗ Failed to generate questions")
            failed += 1

        time.sleep(GEMINI_DELAY)

    log.info(f"\nDone! Success: {success}, Failed: {failed}")


if __name__ == "__main__":
    main()
