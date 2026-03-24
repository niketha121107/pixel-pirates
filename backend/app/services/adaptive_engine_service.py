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

    async def _call_gemini_text(
        self,
        prompt: str,
        max_tokens: int = 1200,
        temperature: float = 0.8,
        timeout: float = 30.0,
        retries: int = 3
    ) -> str:
        """Call Gemini API for text generation (non-JSON) with retry logic"""
        if not self.api_key:
            logger.warning("Gemini API key not configured")
            return ""
        
        url = f"{self.base_url}/models/{self.model}:generateContent"
        
        for attempt in range(retries):
            try:
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
                        "temperature": temperature,
                        "maxOutputTokens": max_tokens,
                    },
                }
                
                async with httpx.AsyncClient(timeout=timeout) as client:
                    res = await client.post(url, params=params, json=payload)
                    
                    # Handle rate limiting with retry
                    if res.status_code == 429:
                        logger.warning(f"Rate limited, attempt {attempt + 1}/{retries}")
                        if attempt < retries - 1:
                            import asyncio
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                            continue
                    
                    if res.status_code in [400, 401, 403]:
                        error_data = res.json() if res.text else {}
                        error_msg = error_data.get("error", {}).get("message", "Unknown error")
                        logger.error(f"Gemini auth error {res.status_code}: {error_msg}")
                        return ""
                    
                    res.raise_for_status()
                    data = res.json()
                    
                    # Extract text from response
                    try:
                        text = data["candidates"][0]["content"]["parts"][0]["text"]
                        logger.debug(f"Gemini API response received ({len(text)} chars)")
                        return text.strip()
                    except (KeyError, IndexError, TypeError) as parse_error:
                        logger.error(f"Failed to parse Gemini response: {parse_error}. Raw: {data}")
                        return ""
                        
            except httpx.TimeoutException as e:
                logger.warning(f"Gemini API timeout (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    import asyncio
                    await asyncio.sleep(1)
                    continue
                return ""
            except httpx.HTTPStatusError as e:
                logger.error(f"Gemini API HTTP error {e.response.status_code}: {e.response.text[:200]}")
                return ""
            except Exception as e:
                logger.error(f"Gemini API call failed (attempt {attempt + 1}/{retries}): {type(e).__name__}: {e}")
                if attempt < retries - 1:
                    import asyncio
                    await asyncio.sleep(1)
                    continue
                return ""
        
        logger.error("Gemini API failed after all retries")
        return ""

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
            # Step 1: Generate response in English first for consistency
            conversation_context = (
                f"You are EduTwin AI, a focused educational tutor. Student name: {user_name}. "
                "Be friendly for greetings, but keep all teaching responses professional, clear, and limited to provided study topics only."
            )
            has_history = bool(history and len(history) > 0)
            
            if history:
                conversation_context += "\n\nRecent conversation:\n"
                for h in history[-6:]:
                    role = h.get("role", "user")
                    content = h.get("content", "")
                    conversation_context += f"{role}: {content}\n"
            
            english_prompt = f"""{conversation_context}

Respond to this message from {user_name} in ENGLISH FIRST:
{message}

Guidelines:
- Accept greeting variants such as hi, hello, hey, hlo, hlw, hii, and heyy.
- If the input is only a greeting, respond in one short, friendly sentence and invite a study-related question.
- If the question is outside provided learning topics, respond exactly with:
    "Sorry, I can only answer questions related to the provided learning topics."
- Use a balanced tone: approachable but not casual-chit-chat, and not overly strict.
- Use a professional, educational style for topic-related answers.
- Give a direct answer first, then concise supporting details
- Keep it concise (about 80-180 words) unless user explicitly asks for depth
- Use practical, accurate examples
- Include code snippets only when useful
- Use clear markdown sections for readability
- Do not engage in general conversation beyond brief greetings.
- Do not answer irrelevant or out-of-context questions.
- If this is a follow-up message, do NOT greet again
- Never re-introduce yourself after the first turn

STRUCTURE RULES (VERY IMPORTANT):
- For concept/explanation questions, use this exact structure:
    ### Quick Answer
    1-2 short sentences.

    ### Key Points
    - 3 to 5 bullet points, one idea per line.

    ### Example
    - If coding-related, provide one short code block.
    - Add 2-4 line explanation after the code block.

    ### Next Step
    - One practical next action + one short follow-up question.

- For short greeting-like requests, briefly redirect to learning topics.
- Do not output one huge paragraph.
- Keep line lengths readable and use spacing between sections."""
            
            # Generate complete English response
            logger.debug(f"Requesting English response from Gemini (timeout: 30s, retries: 3)")
            english_response = await self._call_gemini_text(
                english_prompt,
                max_tokens=2000,
                temperature=0.8,
                timeout=30.0,
                retries=3
            )
            
            if not english_response:
                logger.warning("English response generation failed, using fallback")
                return self._get_fallback_chat_response(message, user_name)
            
            logger.debug(f"English response generated ({len(english_response)} chars)")
            
            # Step 2: If non-English, translate the complete response
            if language and language != "en":
                lang_map = {
                    "hi": "Hindi", "es": "Spanish", "fr": "French", "de": "German",
                    "zh": "Chinese", "ja": "Japanese", "ko": "Korean", "ar": "Arabic",
                    "pt": "Portuguese", "ru": "Russian", "ta": "Tamil", "te": "Telugu",
                    "bn": "Bengali", "kn": "Kannada", "ml": "Malayalam",
                }
                lang_name = lang_map.get(language, language)
                
                translation_prompt = f"""Translate the following English explanation to {lang_name} language.
IMPORTANT:
- Provide COMPLETE and FULL translation - DO NOT SKIP any lines
- Include ALL code examples and explanations
- Keep code syntax unchanged (Python, JavaScript, etc.)
- Explain code line-by-line in {lang_name}
- NO abbreviations or summaries - translate everything in detail
- Maintain all emojis and formatting

English content to translate:
{english_response}"""
                
                translated_response = await self._call_gemini_text(
                    translation_prompt,
                    max_tokens=2500,
                    temperature=0.3,  # Lower temp for consistent translation
                    timeout=30.0,
                    retries=3
                )
                
                if translated_response:
                    logger.debug(f"Translation completed ({len(translated_response)} chars)")
                    return translated_response
                else:
                    logger.warning(f"Translation to {lang_name} failed, returning English")
                    return english_response
            
            return english_response

        except Exception as e:
            logger.error(f"Error in Gemini chat: {type(e).__name__}: {e}")
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
        additional_context: str = "",
        language: str = "en"
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
            
            # Step 1: Generate complete English explanation first
            english_prompt = f"""Create a complete, detailed {user_preferred_style} explanation for: {topic}

Difficulty Level: {difficulty_level}
Learning Style: {user_preferred_style}
Context: {additional_context}

REQUIREMENTS:
- Provide COMPLETE and DETAILED explanation
- ALWAYS include 2-3 working code examples with full explanations
- Explain each code line in detail
- Use {guideline}
- Be comprehensive - include all important details
- Add practical examples and use cases"""
            
            english_explanation = await self._call_gemini_text(
                english_prompt,
                max_tokens=2000,
                temperature=0.7,
                timeout=30.0,
                retries=3
            )
            
            if not english_explanation:
                logger.warning("English explanation generation failed")
                return "Unable to generate explanation at this time."
            
            # Step 2: If non-English, translate the complete explanation
            if language and language != "en":
                lang_map = {
                    "hi": "Hindi", "es": "Spanish", "fr": "French", "de": "German",
                    "zh": "Chinese", "ja": "Japanese", "ko": "Korean", "ar": "Arabic",
                    "pt": "Portuguese", "ru": "Russian", "ta": "Tamil", "te": "Telugu",
                    "bn": "Bengali", "kn": "Kannada", "ml": "Malayalam",
                }
                lang_name = lang_map.get(language, language)
                
                translation_prompt = f"""Translate the following English explanation to {lang_name} language.

CRITICAL REQUIREMENTS:
- TRANSLATE COMPLETELY - provide FULL translation of everything
- DO NOT SKIP any lines, examples, or details
- Include ALL code examples with complete explanations
- Keep code syntax unchanged (Python, JavaScript, Java, etc.)
- Explain code line-by-line in {lang_name}
- NO abbreviations, summaries, or shortened versions
- Match the detail and comprehensiveness of the English original
- Make translation as long and detailed as needed

English explanation to translate:
{english_explanation}"""
                
                translated_explanation = await self._call_gemini_text(
                    translation_prompt,
                    max_tokens=2500,
                    temperature=0.3,  # Lower temp for consistent translation
                    timeout=30.0,
                    retries=3
                )
                
                if translated_explanation:
                    return translated_explanation
                else:
                    logger.warning(f"Translation to {lang_name} failed, returning English")
                    return english_explanation
            
            return english_explanation

        except Exception as e:
            logger.error(f"Error generating personalized explanation: {type(e).__name__}: {e}")
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
