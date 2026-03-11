import json
import re
from typing import Any, Dict, List, Optional
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class AdaptiveEngineService:
    """Gemini-backed adaptive learning and quiz evaluation service."""

    def __init__(self) -> None:
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL
        self.base_url = settings.GEMINI_BASE_URL.rstrip("/")

    async def _generate(self, prompt: str) -> str:
        if not self.api_key:
            logger.warning("Gemini API key not configured")
            return ""

        url = f"{self.base_url}/models/{self.model}:generateContent"
        params = {"key": self.api_key}
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "responseMimeType": "application/json",
            },
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post(url, params=params, json=payload)
                
                # Check for authentication errors
                if res.status_code == 400:
                    error_data = res.json() if res.text else {}
                    error_msg = error_data.get("error", {}).get("message", "")
                    if "API_KEY_INVALID" in error_msg or "API key not valid" in error_msg:
                        logger.error(f"Gemini API authentication failed: {error_msg}")
                        logger.error("Please get a valid API key from https://makersuite.google.com/app/apikey")
                        return ""
                
                res.raise_for_status()
                data = res.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Gemini API HTTP error {e.response.status_code}: {e.response.text[:200]}")
            return ""
        except Exception as e:
            logger.error(f"Gemini API request failed: {e}")
            return ""

        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            return ""

    @staticmethod
    def _extract_json(text: str) -> Optional[Any]:
        if not text:
            return None
        stripped = text.strip()
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            pass

        match = re.search(r"\{[\s\S]*\}|\[[\s\S]*\]", stripped)
        if not match:
            return None
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None

    async def generate_adaptive_quiz(
        self,
        topic_name: str,
        difficulty: str,
        question_count: int,
        user_performance_history: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        prompt = (
            "You are an adaptive quiz generator. Return STRICT JSON array only. "
            "Generate exactly {count} questions for topic '{topic}'. "
            "Difficulty: {difficulty}. "
            "Use user performance history to adjust difficulty and focus weak concepts. "
            "Each item must have: id (string), question (string), options (array of 4 strings), "
            "correctAnswer (integer index 0-3), explanation (string), type ('mcq'). "
            "No markdown, no extra text. "
            "User performance history: {history}"
        ).format(
            count=question_count,
            topic=topic_name,
            difficulty=difficulty,
            history=json.dumps(user_performance_history),
        )

        raw = await self._generate(prompt)
        parsed = self._extract_json(raw)
        if not isinstance(parsed, list):
            return []

        normalized: List[Dict[str, Any]] = []
        for i, q in enumerate(parsed[:question_count]):
            if not isinstance(q, dict):
                continue
            options = q.get("options") if isinstance(q.get("options"), list) else []
            if len(options) < 2:
                continue
            correct = q.get("correctAnswer")
            if not isinstance(correct, int) or correct < 0 or correct >= len(options):
                correct = 0
            normalized.append(
                {
                    "id": q.get("id") or f"adaptive-{i + 1}",
                    "question": str(q.get("question", "")).strip(),
                    "options": [str(x) for x in options[:4]],
                    "correctAnswer": correct,
                    "explanation": str(q.get("explanation", "")).strip(),
                    "type": "mcq",
                }
            )

        return normalized

    async def evaluate_quiz_attempt(
        self,
        topic_name: str,
        percentage: float,
        correct_count: int,
        total_questions: int,
        incorrect_question_ids: List[str],
        preferred_style: str,
    ) -> Dict[str, Any]:
        prompt = (
            "You are an adaptive learning evaluator. Return STRICT JSON object only with keys: "
            "feedback (string), weakAreas (array of objects with concept and recommendation), "
            "nextStep (string). "
            "Context: topic='{topic}', score={score:.1f}%, correct={correct}/{total}, "
            "incorrectQuestionIds={incorrect_ids}, preferredStyle='{style}'."
        ).format(
            topic=topic_name,
            score=percentage,
            correct=correct_count,
            total=total_questions,
            incorrect_ids=json.dumps(incorrect_question_ids),
            style=preferred_style,
        )

        raw = await self._generate(prompt)
        parsed = self._extract_json(raw)
        if not isinstance(parsed, dict):
            return {
                "feedback": "Good attempt. Review incorrect concepts and try again with focused practice.",
                "weakAreas": [],
                "nextStep": "Revise this topic and retake the quiz.",
            }

        weak_areas = parsed.get("weakAreas") if isinstance(parsed.get("weakAreas"), list) else []
        cleaned_weak_areas = []
        for item in weak_areas[:5]:
            if not isinstance(item, dict):
                continue
            cleaned_weak_areas.append(
                {
                    "concept": str(item.get("concept", "General")).strip() or "General",
                    "recommendation": str(item.get("recommendation", "Practice more questions on this concept.")).strip(),
                }
            )

        return {
            "feedback": str(parsed.get("feedback", "Good attempt. Keep practicing.")).strip(),
            "weakAreas": cleaned_weak_areas,
            "nextStep": str(parsed.get("nextStep", "Revise and retake.")).strip(),
        }

    async def chat(
        self,
        message: str,
        history: list = None,
        user_name: str = "Student",
        language: str = "en",
    ) -> str:
        """Generate a conversational AI tutor response using Gemini"""
        if not self.api_key:
            logger.warning("Gemini API key not configured, returning fallback response")
            return self._get_fallback_chat_response(message, user_name)

        try:
            # Build conversation context
            conversation_context = f"You are EduTwin AI, a warm and supportive learning companion. Student name: {user_name}. "
            
            # Add history context if available
            if history:
                conversation_context += "\n\nRecent conversation:\n"
                for h in history[-6:]:  # Last 6 messages for context
                    role = h.get("role", "user")
                    content = h.get("content", "")
                    conversation_context += f"{role}: {content}\n"
            
            lang_instruction = ""
            if language and language != "en":
                lang_map = {
                    "hi": "Hindi", "es": "Spanish", "fr": "French", "de": "German",
                    "zh": "Chinese", "ja": "Japanese", "ko": "Korean", "ar": "Arabic",
                    "pt": "Portuguese", "ru": "Russian", "ta": "Tamil", "te": "Telugu",
                    "bn": "Bengali", "kn": "Kannada", "ml": "Malayalam",
                }
                lang_name = lang_map.get(language, language)
                lang_instruction = f"\n- IMPORTANT: You MUST respond entirely in {lang_name}. Write your complete answer in {lang_name} language only. Do NOT respond in English."

            full_prompt = f"""{conversation_context}

Now respond to this message from {user_name}:
{message}

Guidelines:
- Be warm, encouraging, and patient like a caring friend
- Use simple, clear language with concrete examples
- Add code snippets when helpful
- Use a few emojis to keep things engaging
- If they're stuck, break concepts into smaller steps
- End with encouragement or a follow-up question
- Keep responses focused and under 250 words{lang_instruction}"""

            url = f"{self.base_url}/models/{self.model}:generateContent"
            params = {"key": self.api_key}
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": full_prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.8,
                    "maxOutputTokens": 1200,
                },
            }

            async with httpx.AsyncClient(timeout=25.0) as client:
                res = await client.post(url, params=params, json=payload)
                
                # Handle authentication errors
                if res.status_code in [400, 401, 403]:
                    logger.error(f"Gemini authentication error {res.status_code}: {res.text[:200]}")
                    return self._get_fallback_chat_response(message, user_name)
                
                res.raise_for_status()
                data = res.json()

            try:
                response_text = data["candidates"][0]["content"]["parts"][0]["text"]
                return response_text.strip()
            except (KeyError, IndexError):
                logger.error("Failed to extract chat response from Gemini")
                return self._get_fallback_chat_response(message, user_name)

        except Exception as e:
            logger.error(f"Error in Gemini chat: {e}")
            return self._get_fallback_chat_response(message, user_name)

    def _get_fallback_chat_response(self, message: str, user_name: str) -> str:
        """Provide helpful fallback response when Gemini is unavailable"""
        lower_msg = message.lower()
        
        if "for loop" in lower_msg or "while loop" in lower_msg:
            return f"""Hi {user_name}! 👋

**For Loop** in Python iterates over a sequence:
```python
for i in range(5):
    print(i)  # Prints 0, 1, 2, 3, 4
```

**While Loop** repeats while a condition is True:
```python
count = 0
while count < 3:
    print(count)
    count += 1
```

💡 **Tip**: Use `for` when you know how many times to loop, `while` when you don't!

Want to try writing a loop? Share your code and I'll help! 🚀"""
        
        elif "python" in lower_msg or "programming" in lower_msg:
            return f"""Hey {user_name}! 🌟

I'm here to help you learn programming! Here's what I can do:
- Explain concepts with examples
- Debug your code
- Create practice problems
- Give tips and best practices

What would you like to learn about? Try asking:
- "Explain Python functions with examples"
- "What's the difference between lists and tuples?"
- "Help me understand if-else statements"

I'm excited to learn with you! 💪"""
        
        else:
            return f"""Hi {user_name}! 👋

I'm your AI learning buddy! I can help you with:
✨ Programming concepts (Python, JavaScript, Java, etc.)
🐛 Debugging code
💡 Understanding algorithms
📝 Practice problems

What would you like to learn today? Be specific and I'll give you a clear explanation with examples!

Example: "Explain Python for loops with 3 examples" """

    async def get_personalized_explanation(
        self,
        topic: str,
        user_preferred_style: str,
        difficulty_level: str,
        additional_context: str = ""
    ) -> str:
        """Generate personalized explanation based on user's learning style using Gemini"""
        if not self.api_key:
            return "Gemini API not configured."

        try:
            style_guidelines = {
                "visual": "Use analogies, metaphors, diagrams, and rich visual descriptions",
                "simplified": "Use plain language, step-by-step breakdowns, and avoid jargon",
                "logical": "Focus on technical details, formal definitions, algorithms, and systematic reasoning",
                "analogy": "Use real-world comparisons, everyday examples, and relatable scenarios"
            }
            
            style = user_preferred_style.lower()
            guideline = style_guidelines.get(style, style_guidelines["simplified"])
            
            prompt = f"""Create a {user_preferred_style} explanation for: {topic}

Difficulty Level: {difficulty_level}
Learning Style: {user_preferred_style}
Style Guideline: {guideline}
Additional Context: {additional_context}

Provide an engaging, accurate explanation appropriate for {difficulty_level} level.
Length: 150-300 words. Include a code example if relevant."""

            url = f"{self.base_url}/models/{self.model}:generateContent"
            params = {"key": self.api_key}
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 600,
                },
            }

            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post(url, params=params, json=payload)
                res.raise_for_status()
                data = res.json()

            try:
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            except (KeyError, IndexError):
                return "Unable to generate explanation at this time."

        except Exception as e:
            logger.error(f"Error generating personalized explanation: {e}")
            return "Unable to generate explanation at this time."

    async def generate_mock_test(
        self,
        topics: List[str],
        difficulty_mix: Dict[str, int],
        total_questions: int = 15
    ) -> Dict[str, Any]:
        """Generate comprehensive mock test using Gemini"""
        if not self.api_key:
            return {"questions": [], "metadata": {}}

        try:
            topics_str = ", ".join(topics)
            difficulty_breakdown = ", ".join([f"{level}: {count} questions" for level, count in difficulty_mix.items()])
            
            prompt = f"""Create a comprehensive programming mock test. Return STRICT JSON only.

Topics: {topics_str}
Total Questions: {total_questions}
Difficulty Breakdown: {difficulty_breakdown}

Requirements:
- Mix of conceptual and practical questions
- Include code snippets where appropriate  
- Progressive difficulty
- Real-world scenarios

JSON format:
{{
  "metadata": {{
    "title": "Mock Test: {topics_str}",
    "totalQuestions": {total_questions},
    "estimatedTime": "30 minutes",
    "topics": {json.dumps(topics)}
  }},
  "questions": [
    {{
      "id": "q1",
      "question": "Question text",
      "options": ["A", "B", "C", "D"],
      "correctAnswer": 0,
      "difficulty": "Beginner",
      "topic": "Topic name",
      "explanation": "Why this is correct"
    }}
  ]
}}"""

            url = f"{self.base_url}/models/{self.model}:generateContent"
            params = {"key": self.api_key}
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.5,
                    "maxOutputTokens": 3000,
                    "responseMimeType": "application/json",
                },
            }

            async with httpx.AsyncClient(timeout=35.0) as client:
                res = await client.post(url, params=params, json=payload)
                res.raise_for_status()
                data = res.json()

            try:
                json_text = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = self._extract_json(json_text)
                if isinstance(parsed, dict) and "questions" in parsed:
                    return parsed
                else:
                    return {"questions": [], "metadata": {}}
            except Exception:
                return {"questions": [], "metadata": {}}

        except Exception as e:
            logger.error(f"Error generating mock test: {e}")
            return {"questions": [], "metadata": {}}

    async def analyze_learning_progress(
        self,
        user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze user learning progress and provide recommendations using Gemini"""
        if not self.api_key:
            return {"error": "Gemini API not configured"}

        try:
            prompt = f"""Analyze this student's learning progress. Return STRICT JSON only.

User Data:
{json.dumps(user_data, indent=2)}

Analyze:
1. Learning patterns and strengths
2. Areas needing improvement
3. Recommended next topics
4. Study schedule suggestions
5. Learning style effectiveness

JSON format:
{{
  "strengths": ["strength 1", "strength 2"],
  "weaknesses": ["weakness 1", "weakness 2"],
  "recommendations": ["tip 1", "tip 2"],
  "nextTopics": ["topic 1", "topic 2"],
  "studyPlan": "Personalized study plan text"
}}"""

            url = f"{self.base_url}/models/{self.model}:generateContent"
            params = {"key": self.api_key}
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.4,
                    "maxOutputTokens": 1000,
                    "responseMimeType": "application/json",
                },
            }

            async with httpx.AsyncClient(timeout=25.0) as client:
                res = await client.post(url, params=params, json=payload)
                res.raise_for_status()
                data = res.json()

            try:
                json_text = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = self._extract_json(json_text)
                if isinstance(parsed, dict):
                    return parsed
                else:
                    return {"error": "Failed to parse analysis"}
            except Exception:
                return {"error": "Failed to parse analysis"}

        except Exception as e:
            logger.error(f"Error analyzing learning progress: {e}")
            return {"error": "Analysis unavailable"}

    async def generate_image(self, prompt: str) -> Optional[str]:
        """Generate an educational image using Gemini's image generation.
        Returns base64 encoded image data or None on failure."""
        if not self.api_key:
            return None

        try:
            # Use Gemini's imagen model for image generation
            url = f"{self.base_url}/models/gemini-2.0-flash-exp:generateContent"
            params = {"key": self.api_key}
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": f"Generate a clear, educational diagram or illustration for: {prompt}. "
                                     "The image should be suitable for a programming/computer science student. "
                                     "Use clear labels, simple colors, and organized layout."}
                        ]
                    }
                ],
                "generationConfig": {
                    "responseModalities": ["TEXT", "IMAGE"],
                },
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, params=params, json=payload)
                if res.status_code != 200:
                    logger.warning(f"Image generation returned {res.status_code}")
                    return None
                data = res.json()

            # Extract image from response parts
            parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            for part in parts:
                if "inlineData" in part:
                    return part["inlineData"].get("data")
            return None

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return None


adaptive_engine_service = AdaptiveEngineService()
