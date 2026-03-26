"""
Mock Test Security & Anti-Cheat Service
Handles question generation, violation tracking, and account suspension
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
import json
import httpx
from google import genai
from pymongo import MongoClient
from app.core.config import settings

logger = logging.getLogger(__name__)

class ViolationType(Enum):
    SCREENSHOT = "screenshot"
    COPY_ATTEMPT = "copy_attempt"
    TAB_SWITCH = "tab_switch"

client = MongoClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DATABASE]

class MockTestSecurityService:
    """Handles all mock test security and generation"""
    
    def __init__(self):
        self.genai_client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.gemini_model = settings.GEMINI_MODEL
        self.openrouter_api_key = settings.OPENROUTER_API_KEY
        self.openrouter_model = settings.OPENROUTER_MODEL
        self.max_violations = 10
        self.suspension_duration = 6  # hours
        self.history_collection = db["mock_test_question_history"]
    
    async def generate_mock_test_questions(
        self,
        topic_name: str,
        num_questions: int = 10,
        question_types: List[str] = None,
        history: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Generate mock test questions using Gemini, fallback to OpenRouter, then synthetic"""
        
        if question_types is None:
            question_types = ["multiple_choice", "fill_blank", "short_answer"]
        
        # Normalize topic name for history lookup
        normalized_topic = topic_name.strip().lower()
        
        history_str = ""
        if history:
            history_str = f"""
### ANTI-REPEAT SYSTEM:
- Maintain a running list of ALL questions you have asked in this entire conversation.
- Before generating any new question, check that list.
- If a similar question (same concept, same answer, or same wording) was already asked — SKIP it and generate a different one.
- Never ask the same concept twice even if the wording is slightly different.
- Treat each question as UNIQUE by tracking: topic + concept + correct answer combination.

PREVIOUS QUESTIONS FOR {topic_name}:
""" + "\n".join([f"- {h}" for h in history])

        prompt = f"""Generate a comprehensive mock test with {num_questions} questions for the topic: '{topic_name}'

{history_str}

STRICT REQUIREMENTS:
1. Create {num_questions} questions with the following distribution:
   - {num_questions // 3} Multiple Choice (MCQ) questions
   - {num_questions // 3} Fill-in-the-Blank questions
   - {num_questions // 3} Short Answer questions

2. For EACH question provide:
   - question_type: "multiple_choice", "fill_blank", or "short_answer"
   - question: The question text
   - options (for MCQ only): Array of 4 options [A, B, C, D]
   - correct_answer: The correct answer
   - explanation: Why this is correct and how to understand it
   - difficulty: "easy", "medium", or "hard"
   - points: 1-5 points based on difficulty

3. Make questions:
   - Specific to "{topic_name}"
   - Progressive in difficulty (easy → medium → hard)
   - Comprehensive coverage of the topic
   - Practical and scenario-based where applicable
   - If all easy questions on a topic are exhausted, move to medium/hard variants.

4. ANTI-REPEAT FINAL CHECK:
   - Compare every question you just wrote against the list of PREVIOUS QUESTIONS.
   - If ANY question matches in concept, wording, or answer, REWRITE IT NOW before returning the JSON.

Return ONLY valid JSON array with no additional text:
[
  {{
    "question_type": "multiple_choice",
    "question": "...",
    "options": ["...", "...", "...", "..."],
    "correct_answer": "...",
    "explanation": "...",
    "difficulty": "easy",
    "points": 2
  }},
  ...
]"""
        
        logger.info(f"Generating {num_questions} mock test questions for topic: {topic_name}")
        
        # Step 1: Try Gemini first
        try:
            response = await asyncio.to_thread(
                self._call_gemini,
                prompt
            )
            
            # Parse response
            try:
                # Extract JSON from response (handle potential markdown code blocks)
                content = response.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                questions = json.loads(content)
                logger.info(f"✅ Generated {len(questions)} questions using Gemini AI for {topic_name}")
                return questions
            except json.JSONDecodeError:
                logger.warning("Failed to parse Gemini response as JSON, trying OpenRouter...")
        except Exception as e:
            error_msg = str(e).lower()
            if "quota" in error_msg or "429" in error_msg:
                logger.warning(f"⚠️  Gemini quota exceeded, falling back to OpenRouter: {e}")
            else:
                logger.warning(f"⚠️  Gemini API error, trying OpenRouter: {e}")
        
        # Step 2: Try OpenRouter API as fallback
        if self.openrouter_api_key:
            try:
                questions = await self._generate_with_openrouter(prompt, num_questions)
                if questions:
                    logger.info(f"✅ Generated {len(questions)} questions using OpenRouter API for {topic_name}")
                    return questions
            except Exception as e:
                logger.warning(f"⚠️  OpenRouter API error: {e}")
        
        # Step 3: Fall back to synthetic questions
        logger.warning(f"⚠️  All AI APIs failed, using synthetic questions for {topic_name}")
        return self._create_fallback_questions(topic_name, num_questions)
    
    async def _generate_with_openrouter(self, prompt: str, num_questions: int) -> Optional[List[Dict[str, Any]]]:
        """Generate questions using OpenRouter API (Claude or similar)"""
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "model": self.openrouter_model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.5,
                "max_tokens": 2000,
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    
                    # Extract JSON from response
                    try:
                        if "```json" in content:
                            content = content.split("```json")[1].split("```")[0]
                        elif "```" in content:
                            content = content.split("```")[1].split("```")[0]
                        
                        questions = json.loads(content)
                        return questions
                    except json.JSONDecodeError:
                        logger.error("Failed to parse OpenRouter response as JSON")
                        return None
                else:
                    logger.error(f"OpenRouter API error {response.status_code}: {response.text[:200]}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error calling OpenRouter API: {e}")
            return None
    
    def _call_gemini(self, prompt: str) -> str:
        """Synchronous wrapper for Gemini API call"""
        response = self.genai_client.models.generate_content(
            model=self.gemini_model,
            contents=prompt,
        )
        return response.text
    
    def _create_fallback_questions(self, topic: str, count: int) -> List[Dict[str, Any]]:
        """Create high-quality fallback questions if AI fails"""
        
        questions = []
        for i in range(count):
            q_type = ["multiple_choice", "fill_blank", "short_answer"][i % 3]
            
            if q_type == "multiple_choice":
                questions.append({
                    "question_type": "multiple_choice",
                    "question": f"Which of the following is a primary feature or concept of {topic}? (Question {i+1})",
                    "options": [
                        f"The core {topic} implementation strategy",
                        f"A secondary {topic} utility function",
                        f"A common {topic} configuration option",
                        f"An advanced {topic} performance optimization"
                    ],
                    "correct_answer": f"The core {topic} implementation strategy",
                    "explanation": f"Understanding the core implementation of {topic} is essential.",
                    "difficulty": "medium",
                    "points": 2,
                    "topic": topic
                })
            elif q_type == "fill_blank":
                questions.append({
                    "question_type": "fill_blank",
                    "question": f"In {topic}, the most important fundamental principle to follow is ___________. (Question {i+1})",
                    "correct_answer": f"correct {topic} usage",
                    "explanation": f"Following {topic} best practices ensures reliable code.",
                    "difficulty": "medium",
                    "points": 2,
                    "topic": topic
                })
            else:
                questions.append({
                    "question_type": "short_answer",
                    "question": f"Briefly explain a common use-case for {topic} in modern development. (Question {i+1})",
                    "correct_answer": f"A clear explanation of how {topic} solves specific problems.",
                    "explanation": f"Real-world application of {topic} is a key skill.",
                    "difficulty": "hard",
                    "points": 3,
                    "topic": topic
                })
        
        return questions
    
    async def record_violation(
        self,
        user_id: str,
        violation_type: ViolationType
    ) -> Dict[str, Any]:
        """Record a user violation during mock test"""
        
        violations_collection = db["mock_test_violations"]
        users_collection = db["users"]
        
        # Get current violation count
        user = await asyncio.to_thread(
            lambda: users_collection.find_one({"_id": user_id})
        )
        
        current_violations = user.get("mock_test_violations", 0) if user else 0
        current_violations += 1
        
        # Record violation
        violation_record = {
            "user_id": user_id,
            "violation_type": violation_type.value,
            "timestamp": datetime.utcnow(),
            "violation_count": current_violations
        }
        
        await asyncio.to_thread(
            violations_collection.insert_one,
            violation_record
        )
        
        # Update user document
        await asyncio.to_thread(
            lambda: users_collection.update_one(
                {"_id": user_id},
                {
                    "$set": {
                        "mock_test_violations": current_violations,
                        "last_violation_time": datetime.utcnow()
                    }
                }
            )
        )
        
        # Check if suspension needed
        is_suspended = False
        suspension_until = None
        
        if current_violations >= (self.max_violations + 1):  # 11th violation
            suspension_until = datetime.utcnow() + timedelta(hours=self.suspension_duration)
            
            await asyncio.to_thread(
                lambda: users_collection.update_one(
                    {"_id": user_id},
                    {
                        "$set": {
                            "mock_test_suspended": True,
                            "mock_test_suspension_until": suspension_until,
                            "mock_test_violations": 0  # Reset after suspension
                        }
                    }
                )
            )
            
            is_suspended = True
            logger.warning(f"⚠️ USER {user_id} SUSPENDED FOR {self.suspension_duration}h after {current_violations} violations")
        
        return {
            "violation_count": current_violations,
            "is_suspended": is_suspended,
            "suspension_until": suspension_until,
            "warning_number": min(current_violations, self.max_violations)
        }
    
    async def check_suspension_status(self, user_id: str) -> Dict[str, Any]:
        """Check if user is suspended and lift suspension if time passed"""
        
        users_collection = db["users"]
        
        user = await asyncio.to_thread(
            lambda: users_collection.find_one({"_id": user_id})
        )
        
        if not user:
            return {"is_suspended": False, "violations": 0}
        
        is_suspended = user.get("mock_test_suspended", False)
        suspension_until = user.get("mock_test_suspension_until")
        
        # Check if suspension should be lifted
        if is_suspended and suspension_until and datetime.utcnow() > suspension_until:
            logger.info(f"✅ Lifting suspension for user {user_id} - auto-resetting violations")
            
            await asyncio.to_thread(
                lambda: users_collection.update_one(
                    {"_id": user_id},
                    {
                        "$set": {
                            "mock_test_suspended": False,
                            "mock_test_violations": 0,
                            "mock_test_suspension_until": None
                        }
                    }
                )
            )
            
            return {
                "is_suspended": False,
                "violations": 0,
                "suspension_lifted": True
            }
        
        return {
            "is_suspended": is_suspended,
            "violations": user.get("mock_test_violations", 0),
            "suspension_until": suspension_until
        }
    
    async def get_mock_test_rules(self) -> List[str]:
        """Get mock test rules to display to users"""
        
        return [
            "1. Do NOT take screenshots during the test - they will be detected and recorded as violations.",
            "2. Do NOT copy or paste questions - this is monitored and logged as a violation.",
            "3. Do NOT switch tabs or windows - tab switching is detected (3 warnings = suspension review).",
            "4. Complete the entire test without leaving the page - you cannot navigate away until finished.",
            f"5. You have {self.max_violations} warnings. The 11th violation will suspend your account for {self.suspension_duration} hours.",
            "6. All activities are monitored by our anti-cheat system for fairness and integrity.",
            "7. Answers are automatically saved - try not to refresh the page.",
            "8. After completing the test, review your answers before submitting.",
            "9. Results will show detailed explanations for each question.",
            "10. Your test attempts and violation records will be saved for review by administrators."
        ]

    async def save_generated_questions(self, user_id: str, topic: str, questions: List[Dict[str, Any]]):
        """Save generated question titles to prevent repetition"""
        try:
            # Normalize topic name
            normalized_topic = topic.strip().lower()
            
            titles = [q.get("question") for q in questions if q.get("question")]
            if titles:
                await asyncio.to_thread(
                    self.history_collection.update_one,
                    {"user_id": user_id, "topic": normalized_topic},
                    {"$push": {"questions": {"$each": titles, "$slice": -100}}},  # Keep last 100
                    upsert=True
                )
        except Exception as e:
            logger.error(f"Error saving question history: {e}")

    async def get_user_question_history(self, user_id: str, topic: str) -> List[str]:
        """Get previously generated question titles for a user and topic"""
        try:
            # Normalize topic name
            normalized_topic = topic.strip().lower()
            
            record = await asyncio.to_thread(
                self.history_collection.find_one,
                {"user_id": user_id, "topic": normalized_topic}
            )
            return record.get("questions", []) if record else []
        except Exception as e:
            logger.error(f"Error fetching question history: {e}")
            return []

# Initialize service
mock_test_service = MockTestSecurityService()