#!/usr/bin/env python
"""
Comprehensive AI Integration Service
Generates ALL content on-demand using Gemini AI:
- Study materials
- Quiz questions
- Mock tests
- Progress recommendations
- Explanations
"""

import os
import json
import asyncio
import httpx
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.core.config import Settings

logger = logging.getLogger(__name__)

# Load configuration
settings = Settings()

class AIContentGenerator:
    """Generate all learning content using Gemini AI"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL
        self.base_url = settings.GEMINI_BASE_URL
    
    async def call_gemini(
        self, 
        prompt: str, 
        temperature: float = 0.7, 
        max_tokens: int = 2048,
        retries: int = 3
    ) -> str:
        """Call Gemini API with retry logic"""
        
        for attempt in range(retries):
            try:
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
                        "temperature": temperature,
                        "maxOutputTokens": max_tokens,
                    }
                }
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(url, params=params, json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if "candidates" in data and len(data["candidates"]) > 0:
                            return data["candidates"][0]["content"]["parts"][0]["text"]
                    
                    elif response.status_code == 429:  # Rate limit
                        if attempt < retries - 1:
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                            continue
                    
                    logger.error(f"Gemini API error {response.status_code}: {response.text[:200]}")
                    
            except asyncio.TimeoutError:
                logger.warning(f"Timeout attempt {attempt + 1}/{retries}")
                if attempt < retries - 1:
                    await asyncio.sleep(1)
                    continue
            except Exception as e:
                logger.error(f"Error calling Gemini: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(1)
                    continue
        
        return ""
    
    def _clean_json(self, text: str) -> str:
        """Extract JSON from response, removing markdown code blocks"""
        text = text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        return text.strip()
    
    async def generate_study_material(
        self,
        topic_name: str,
        language: str = "Python",
        difficulty: str = "Intermediate"
    ) -> Dict[str, Any]:
        """Generate comprehensive study material for a topic"""
        
        prompt = f"""Generate comprehensive study material for the topic "{topic_name}" in {language} programming.
        
Topic: {topic_name}
Language: {language}
Difficulty Level: {difficulty}

Provide information as valid JSON with these fields:
- "overview": 2-3 sentence overview
- "explanation": Detailed explanation with concepts and principles  
- "syntax": Show syntax and code format
- "example": Practical working code example with comments
- "advantages": Key benefits (list with bullet points)
- "disadvantages": Limitations and drawbacks
- "realWorldApplication": How it's used in real projects

Return ONLY valid JSON object, no markdown code blocks."""
        
        try:
            response = await self.call_gemini(prompt, max_tokens=2048)
            response = self._clean_json(response)
            
            try:
                data = json.loads(response)
                
                # Ensure all expected fields exist
                material = {
                    "overview": data.get("overview", f"Overview of {topic_name}"),
                    "explanation": data.get("explanation", ""),
                    "syntax": data.get("syntax", ""),
                    "example": data.get("example", data.get("codeExample", "")),
                    "advantages": data.get("advantages", ""),
                    "disadvantages": data.get("disadvantages", ""),
                    "realWorldApplication": data.get("realWorldApplication", data.get("real_world_application", ""))
                }
                
                return {
                    "success": True,
                    "data": material,
                    "generatedAt": datetime.now().isoformat()
                }
            except json.JSONDecodeError as je:
                logger.error(f"Failed to parse study material JSON: {je}")
                logger.error(f"Response: {response[:200]}")
                return {"success": False, "error": "Failed to parse JSON response"}
        
        except Exception as e:
            logger.error(f"Error generating study material: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_explanations(
        self,
        topic_name: str,
        styles: List[str] = None
    ) -> Dict[str, Dict[str, str]]:
        """Generate multiple explanation styles for a topic"""
        
        if styles is None:
            styles = ["simplified", "logical", "visual", "analogy"]
        
        explanations = {}
        
        for style in styles:
            style_prompts = {
                "simplified": f"Explain '{topic_name}' in very simple language for absolute beginners. Use everyday examples and avoid jargon. Keep under 250 words.",
                
                "logical": f"Provide a step-by-step logical explanation of '{topic_name}'. Start with fundamentals and build up. Explain the 'why' and 'how'. Keep under 300 words.",
                
                "visual": f"Describe '{topic_name}' in a way that could be visualized with flowcharts, diagrams, or ASCII art. Include key visual elements and their relationships. Keep under 300 words.",
                
                "analogy": f"Explain '{topic_name}' using real-world analogies and comparisons. Make it relatable and memorable by comparing to everyday situations. Keep under 250 words."
            }
            
            prompt = style_prompts.get(style, style_prompts["simplified"])
            
            try:
                content = await self.call_gemini(prompt, temperature=0.6, max_tokens=400)
                explanations[style] = {
                    "title": f"{style.capitalize()} Explanation",
                    "content": content.strip(),
                    "style": style
                }
            except Exception as e:
                logger.error(f"Error generating {style} explanation: {e}")
                explanations[style] = {
                    "title": f"{style.capitalize()} Explanation",
                    "content": f"Error generating {style} explanation",
                    "style": style
                }
        
        return explanations
    
    async def generate_quiz_questions(
        self,
        topic_name: str,
        num_questions: int = 5,
        difficulty: str = "mixed"
    ) -> List[Dict[str, Any]]:
        """Generate multiple-choice quiz questions"""
        
        prompt = f"""TASK: Generate {num_questions} quiz questions about {topic_name}.

OUTPUT FORMAT - JSON ARRAY ONLY (no other text, no markdown):
[
  {{
    "question": "question text",
    "options": ["opt1", "opt2", "opt3", "opt4"],
    "correctAnswer": 0,
    "explanation": "explanation",
    "difficulty": "easy"
  }}
]

REQUIREMENTS:
- Exactly {num_questions} questions in array
- Each question must have exactly 4 unique options
- correctAnswer is 0, 1, 2, or 3 (index of correct option)
- difficulty: easy|medium|hard (not "mixed")
- explanation: one simple sentence

CRITICAL: Output ONLY the JSON array. Nothing else. No markdown. No code blocks. Start with [ end with ]."""
        
        try:
            response = await self.call_gemini(prompt, max_tokens=2048)
            response = self._clean_json(response)
            
            # Try to parse JSON
            try:
                questions = json.loads(response)
            except json.JSONDecodeError as je:
                logger.error(f"JSON parse error: {je}. Response: {response[:200]}")
                return []
            
            # If response is dict, check for 'questions' key
            if isinstance(questions, dict):
                questions = questions.get("questions", [])
            
            # Validate and normalize
            validated_questions = []
            for i, q in enumerate(questions, 1):
                if not isinstance(q, dict):
                    continue
                
                # Extract question text (support multiple field names)
                question_text = (
                    q.get("question") or 
                    q.get("question_text") or 
                    q.get("text") or 
                    ""
                )
                
                # Extract options (support array or dict format)
                options = q.get("options", [])
                if isinstance(options, dict):
                    options = list(options.values())
                
                # Extract correct answer
                correct_answer = q.get("correctAnswer") or q.get("correct_answer") or 0
                if isinstance(correct_answer, str):
                    try:
                        correct_answer = int(correct_answer)
                    except:
                        correct_answer = 0
                
                # Only add if has required fields
                if question_text and isinstance(options, list) and len(options) == 4:
                    validated_questions.append({
                        "id": f"q{i}",
                        "question": question_text,
                        "options": options[:4],  # Ensure exactly 4
                        "correctAnswer": max(0, min(3, correct_answer)),  # Clamp to 0-3
                        "correctIdx": max(0, min(3, correct_answer)),
                        "explanation": q.get("explanation", ""),
                        "difficulty": q.get("difficulty", "medium"),
                        "type": "mcq"
                    })
            
            if not validated_questions:
                logger.warning(f"No valid questions extracted from quiz generation")
            
            return validated_questions[:num_questions]
        
        except Exception as e:
            logger.error(f"Error generating quiz: {e}")
            return []
    
    async def generate_mock_test(
        self,
        topics: List[str],
        total_questions: int = 20,
        difficulty_mix: Dict[str, int] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive mock test"""
        
        if difficulty_mix is None:
            difficulty_mix = {
                "easy": 5,
                "medium": 10,
                "hard": 5
            }
        
        topics_str = ", ".join(topics)
        difficulty_str = " ".join([f"{level}: {count}" for level, count in difficulty_mix.items()])
        
        prompt = f"""Create a comprehensive programming mock test. Return ONLY valid JSON.

Topics: {topics_str}
Total Questions: {total_questions}
Difficulty Breakdown: {difficulty_str}

Requirements:
- Mix of conceptual and practical questions
- Include code snippets where relevant
- Progressive difficulty from easy to hard
- Real-world programming scenarios
- Each question must test meaningful knowledge

Return format:
{{
  "metadata": {{
    "title": "Full Mock Test: {topics_str}",
    "totalQuestions": {total_questions},
    "estimatedTime": "45 minutes",
    "topics": {json.dumps(topics)},
    "difficulty": {json.dumps(difficulty_mix)}
  }},
  "questions": [
    {{
      "id": "q1",
      "question": "Question text",
      "options": ["A) Option A", "B) Option B", "C) Option C", "D) Option D"],
      "correctIdx": 0,
      "correctAnswer": "A) Option A",
      "difficulty": "easy",
      "topic": "Topic name",
      "explanation": "Why this answer is correct and how to understand it",
      "type": "mcq"
    }}
  ]
}}"""
        
        try:
            response = await self.call_gemini(prompt, max_tokens=3000)
            response = self._clean_json(response)
            test_data = json.loads(response)
            
            # Ensure we have the right structure
            if "questions" in test_data:
                return {
                    "success": True,
                    "data": test_data,
                    "generatedAt": datetime.now().isoformat()
                }
        
        except Exception as e:
            logger.error(f"Error generating mock test: {e}")
        
        return {"success": False, "error": "Failed to generate mock test"}
    
    async def generate_progress_recommendation(
        self,
        topic_name: str,
        user_score: float,
        weak_areas: List[str] = None
    ) -> Dict[str, str]:
        """Generate personalized progress recommendations"""
        
        weak_areas_str = ", ".join(weak_areas) if weak_areas else "general concepts"
        
        prompt = f"""You are an adaptive learning advisor. Provide personalized learning recommendations.

Context:
- Topic: {topic_name}
- User's Test Score: {user_score:.1f}%
- Weak Areas: {weak_areas_str}

Provide recommendations in JSON format:
{{
  "overallFeedback": "Personalized feedback based on their performance",
  "strengths": ["What they did well"],
  "areasToImprove": ["Specific areas they should focus on"],
  "nextSteps": ["Concrete recommended next steps"],
  "resources": "Suggested study approach or additional resources",
  "motivationalMessage": "Encouraging message to keep them motivated"
}}

Make recommendations specific, actionable, and encouraging."""
        
        try:
            response = await self.call_gemini(prompt, temperature=0.6, max_tokens=1000)
            response = self._clean_json(response)
            recommendations = json.loads(response)
            return recommendations
        
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return {
                "overallFeedback": "Keep practicing! Review the weaker concepts and try again.",
                "strengths": ["You're making progress"],
                "areasToImprove": weak_areas or ["Review the topic thoroughly"],
                "nextSteps": ["Practice more questions", "Review explanations"],
                "resources": "Use all available learning materials",
                "motivationalMessage": "Don't give up! Learning takes time."
            }
    
    async def generate_content_explanation(
        self,
        topic_name: str,
        concept: str,
        context: str = ""
    ) -> str:
        """Generate explanation for specific concept"""
        
        prompt = f"""Explain the concept of "{concept}" in the context of {topic_name} programming.

Context: {context}

Provide:
1. What is {concept}?
2. Why is it important in {topic_name}?
3. How to use it effectively?
4. Common pitfalls to avoid

Keep the explanation clear, concise, and practical."""
        
        try:
            return await self.call_gemini(prompt, temperature=0.7, max_tokens=800)
        except Exception as e:
            logger.error(f"Error generating concept explanation: {e}")
            return f"Sorry, unable to generate explanation for {concept} at this time."


# Initialize global generator
ai_generator = AIContentGenerator()
