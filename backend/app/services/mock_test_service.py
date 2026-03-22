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
import google.generativeai as genai
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
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.gemini_model = settings.GEMINI_MODEL
        self.openrouter_api_key = settings.OPENROUTER_API_KEY
        self.openrouter_model = settings.OPENROUTER_MODEL
        self.max_violations = 10
        self.suspension_duration = 6  # hours
    
    async def generate_mock_test_questions(
        self,
        topic_name: str,
        num_questions: int = 10,
        question_types: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Generate mock test questions using Gemini, fallback to OpenRouter, then synthetic"""
        
        if question_types is None:
            question_types = ["multiple_choice", "fill_blank", "short_answer"]
        
        prompt = f"""Generate a comprehensive mock test with {num_questions} questions for the topic: '{topic_name}'

REQUIREMENTS:
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
        model = genai.GenerativeModel(self.gemini_model)
        response = model.generate_content(prompt)
        return response.text
    
    def _create_fallback_questions(self, topic: str, count: int) -> List[Dict[str, Any]]:
        """Create fallback questions if Gemini fails"""
        questions = []
        for i in range(count):
            q_type = ["multiple_choice", "fill_blank", "short_answer"][i % 3]
            
            if q_type == "multiple_choice":
                questions.append({
                    "question_type": "multiple_choice",
                    "question": f"What is a fundamental concept in {topic}? (Question {i+1})",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option A",
                    "explanation": f"This is a fundamental concept in {topic}.",
                    "difficulty": ["easy", "medium", "hard"][i % 3],
                    "points": (i % 3) + 1
                })
            elif q_type == "fill_blank":
                questions.append({
                    "question_type": "fill_blank",
                    "question": f"In {topic}, the key principle is ___________. (Question {i+1})",
                    "correct_answer": "fundamental concept",
                    "explanation": f"The key principle involves understanding the basics of {topic}.",
                    "difficulty": ["easy", "medium", "hard"][i % 3],
                    "points": (i % 3) + 1
                })
            else:
                questions.append({
                    "question_type": "short_answer",
                    "question": f"Explain how {topic} is used in real-world scenarios. (Question {i+1})",
                    "correct_answer": "Any reasonable explanation involving practical applications",
                    "explanation": f"{topic} has many practical applications in industry.",
                    "difficulty": "medium",
                    "points": 3
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

# Initialize service
mock_test_service = MockTestSecurityService()
