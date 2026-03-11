import httpx
import json
from typing import List, Dict, Any, Optional
import logging
from app.core.config import settings
from app.models import QuizQuestion

logger = logging.getLogger(__name__)

class OpenRouterService:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        self.model = settings.OPENROUTER_MODEL
        self.ollama_base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.ollama_model = settings.OLLAMA_MODEL
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": settings.API_BASE_URL,
            "X-Title": "Pixel Pirates Learning Platform",
            "Content-Type": "application/json"
        }

    async def _chat_with_ollama(self, message: str, history: list = None, user_name: str = "Student") -> str:
        """Try local Ollama first so chatbot can work without cloud API keys."""
        if not self.ollama_model:
            return ""

        try:
            sys_prompt = (
                "You are EduTwin AI, a helpful coding tutor. "
                f"Student name: {user_name}. "
                "Answer clearly, with concrete examples, and keep answers relevant to the exact question. "
                "Do not repeat the same answer for different questions."
            )

            messages = [{"role": "system", "content": sys_prompt}]
            if history:
                messages.extend(history[-8:])
            messages.append({"role": "user", "content": message})

            async with httpx.AsyncClient(timeout=25.0) as client:
                response = await client.post(
                    f"{self.ollama_base_url}/api/chat",
                    json={
                        "model": self.ollama_model,
                        "messages": messages,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                        },
                    },
                )

            if response.status_code != 200:
                return ""

            data = response.json()
            return (data.get("message") or {}).get("content", "").strip()
        except Exception as e:
            logger.info(f"Ollama chat unavailable: {e}")
            return ""
    
    async def generate_adaptive_quiz(
        self,
        topic: str,
        difficulty: str,
        user_performance_history: List[Dict[str, Any]],
        question_count: int = 10
    ) -> List[Dict[str, Any]]:
        """Generate adaptive quiz questions based on user performance"""
        try:
            # Analyze user performance to determine focus areas
            weak_areas = self._analyze_weak_areas(user_performance_history)
            
            prompt = self._build_adaptive_quiz_prompt(
                topic, difficulty, weak_areas, question_count
            )
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert educational content creator specializing in programming and computer science. Generate challenging but fair quiz questions."
                            },
                            {
                                "role": "user", 
                                "content": prompt
                            }
                        ],
                        "temperature": 0.7,
                        "max_tokens": 2000
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    return self._parse_quiz_json(content)
                else:
                    logger.error(f"OpenRouter API error: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error generating adaptive quiz: {e}")
            return []
    
    async def generate_mock_test(
        self,
        topics: List[str],
        difficulty_mix: Dict[str, int],  # {"Beginner": 5, "Intermediate": 3, "Advanced": 2}
        total_questions: int = 15
    ) -> Dict[str, Any]:
        """Generate comprehensive mock test"""
        try:
            prompt = self._build_mock_test_prompt(topics, difficulty_mix, total_questions)
            
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions", 
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are creating a comprehensive programming assessment. Focus on practical knowledge, problem-solving, and code understanding."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.6,
                        "max_tokens": 3000
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    return self._parse_mock_test_json(content)
                else:
                    logger.error(f"OpenRouter API error: {response.status_code}")
                    return {"questions": [], "metadata": {}}
                    
        except Exception as e:
            logger.error(f"Error generating mock test: {e}")
            return {"questions": [], "metadata": {}}
    
    async def chat(
        self,
        message: str,
        history: list = None,
        user_name: str = "Student",
    ) -> str:
        """Generate a conversational AI tutor response"""
        try:
            # Prefer local Llama (Ollama) if available.
            ollama_response = await self._chat_with_ollama(message=message, history=history, user_name=user_name)
            if ollama_response:
                return ollama_response

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are EduTwin AI, a warm and supportive learning buddy on the Pixel Pirates platform. "
                        f"The student's name is {user_name}. "
                        "Talk like a caring friend — be casual, encouraging, and patient. "
                        "Use simple language. It's okay to use a few emojis to keep things fun. "
                        "If they seem stressed, reassure them that learning takes time and it's totally normal to struggle. "
                        "Give clear, bite-sized explanations with code examples when helpful. "
                        "Always end with an encouraging note or a follow-up question to keep the conversation going. "
                        "Never be condescending. Celebrate their curiosity."
                    ),
                },
            ]

            # Append recent conversation history (last 10 messages)
            if history:
                for h in history[-10:]:
                    messages.append({"role": h["role"], "content": h["content"]})

            messages.append({"role": "user", "content": message})

            logger.info(f"Sending chat request to OpenRouter (model={self.model}, msgs={len(messages)})")

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.8,
                        "max_tokens": 1200,
                    },
                )

                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"].strip()
                    # Some thinking models wrap output in <think> tags — strip those
                    if "<think>" in content:
                        import re
                        content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
                    logger.info("OpenRouter chat response received successfully")
                    return content
                else:
                    body = response.text[:500]
                    logger.error(f"OpenRouter chat API error {response.status_code}: {body}")
                    return ""

        except Exception as e:
            logger.error(f"Error in AI chat: {e}")
            return ""

    async def get_personalized_explanation(
        self,
        topic: str,
        user_preferred_style: str,
        difficulty_level: str,
        additional_context: str = ""
    ) -> str:
        """Generate personalized explanation based on user's learning style"""
        try:
            prompt = f"""
            Create a {user_preferred_style} explanation for the topic: {topic}
            
            Difficulty Level: {difficulty_level}
            Learning Style: {user_preferred_style}
            Additional Context: {additional_context}
            
            Style Guidelines:
            - Visual: Use analogies, metaphors, and visual descriptions
            - Simplified: Use simple language, step-by-step breakdowns
            - Logical: Focus on technical details, formal definitions, algorithms  
            - Analogy: Use real-world comparisons and everyday examples
            
            Keep the explanation engaging, accurate, and appropriate for the difficulty level.
            Length: 150-300 words.
            """
            
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system", 
                                "content": "You are an expert programming educator who adapts explanations to different learning styles."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.8,
                        "max_tokens": 500
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    return "Unable to generate personalized explanation at this time."
                    
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return "Unable to generate personalized explanation at this time."
    
    async def analyze_learning_progress(
        self,
        user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze user learning progress and provide recommendations"""
        try:
            prompt = f"""
            Analyze this student's learning progress and provide recommendations:
            
            User Data:
            {json.dumps(user_data, indent=2)}
            
            Please analyze:
            1. Learning patterns and strengths
            2. Areas needing improvement  
            3. Recommended next topics
            4. Study schedule suggestions
            5. Learning style effectiveness
            
            Provide response in JSON format with keys: strengths, weaknesses, recommendations, nextTopics, studyPlan
            """
            
            async with httpx.AsyncClient(timeout=25.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an AI learning analytics expert. Provide detailed, actionable insights."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.5,
                        "max_tokens": 1000
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        return {"error": "Failed to parse analysis"}
                else:
                    return {"error": "API request failed"}
                    
        except Exception as e:
            logger.error(f"Error analyzing progress: {e}")
            return {"error": "Analysis unavailable"}
    
    def _build_adaptive_quiz_prompt(
        self, topic: str, difficulty: str, weak_areas: List[str], count: int
    ) -> str:
        focus_areas = ", ".join(weak_areas) if weak_areas else "general concepts"
        
        return f"""
        Generate {count} multiple choice quiz questions for: {topic}
        
        Difficulty: {difficulty}
        Focus on these areas based on user's previous performance: {focus_areas}
        
        Each question should have:
        - Clear, unambiguous question text
        - 4 multiple choice options
        - One correct answer
        - Brief explanation of the correct answer
        
        Format as JSON array:
        [
          {{
            "id": "q1",
            "question": "Question text here?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correctAnswer": 0,
            "explanation": "Why this answer is correct..."
          }}
        ]
        """
    
    def _build_mock_test_prompt(
        self, topics: List[str], difficulty_mix: Dict[str, int], total: int
    ) -> str:
        topics_str = ", ".join(topics)
        difficulty_breakdown = ", ".join([f"{level}: {count} questions" for level, count in difficulty_mix.items()])
        
        return f"""
        Create a comprehensive mock test covering: {topics_str}
        
        Total Questions: {total}
        Difficulty Breakdown: {difficulty_breakdown}
        
        Requirements:
        - Mix of conceptual and practical questions
        - Include code snippets where appropriate
        - Progressive difficulty within each section
        - Real-world application scenarios
        
        Format as JSON:
        {{
          "metadata": {{
            "title": "Mock Test Title",
            "totalQuestions": {total},
            "estimatedTime": "X minutes",
            "topics": {topics}
          }},
          "questions": [
            {{
              "id": "q1", 
              "question": "Question text",
              "options": ["A", "B", "C", "D"],
              "correctAnswer": 0,
              "difficulty": "Beginner|Intermediate|Advanced",
              "topic": "Topic Name",
              "explanation": "Explanation text"
            }}
          ]
        }}
        """
    
    def _analyze_weak_areas(self, performance_history: List[Dict[str, Any]]) -> List[str]:
        """Analyze performance history to identify weak areas"""
        weak_areas = []
        
        if not performance_history:
            return weak_areas
        
        # Simple analysis - in production, this would be more sophisticated
        for performance in performance_history:
            if performance.get("score", 0) < 70:  # Below 70% is considered weak
                topic = performance.get("topic", "")
                if topic and topic not in weak_areas:
                    weak_areas.append(topic)
        
        return weak_areas[:3]  # Focus on top 3 weak areas
    
    def _parse_quiz_json(self, content: str) -> List[Dict[str, Any]]:
        """Parse AI-generated quiz JSON"""
        try:
            # Try to extract JSON from response
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = content[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return []
        except Exception as e:
            logger.error(f"Error parsing quiz JSON: {e}")
            return []
    
    def _parse_mock_test_json(self, content: str) -> Dict[str, Any]:
        """Parse AI-generated mock test JSON"""
        try:
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = content[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return {"questions": [], "metadata": {}}
        except Exception as e:
            logger.error(f"Error parsing mock test JSON: {e}")
            return {"questions": [], "metadata": {}}

# Global instance
openrouter_service = OpenRouterService()