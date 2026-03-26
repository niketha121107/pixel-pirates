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
        styles: Optional[List[str]] = None
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
        difficulty: str = "mixed",
        history: Optional[List[str]] = None,
        include_correct_answer: bool = True
    ) -> List[Dict[str, Any]]:
        """Generate multiple-choice quiz questions
        
        Args:
            topic_name: Name of the topic
            num_questions: Number of questions to generate
            difficulty: Question difficulty level
            history: List of previous questions to avoid repetition
            include_correct_answer: Whether to include correct answers in response (use False for practice mode)
        """
        
        history_str = ""
        if history:
            history_str = f"\n\nCRITICAL: DO NOT repeat or generate any of these previous questions:\n" + "\n".join([f"- {h}" for h in history])

        prompt = f"""TASK: Generate {num_questions} quiz questions about {topic_name}.{history_str}

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
- If all easy questions on this topic are exhausted, move to medium/hard variants.

### ANTI-REPEAT SYSTEM:
- Maintain a running list of ALL questions you have asked in this entire conversation.
- Before generating any new question, check that list.
- If a similar question (same concept, same answer, or same wording) was already asked — SKIP it and generate a different one.
- Never ask the same concept twice even if the wording is slightly different.
- Treat each question as UNIQUE by tracking: topic + concept + correct answer combination.

PREVIOUS QUESTIONS FOR {topic_name}:
{history_str}

CRITICAL: Output ONLY the JSON array. Nothing else. No markdown. No code blocks. Start with [ end with ].
Perform a FINAL CHECK: if any generated question matches a previous concept, REWRITE IT.
"""
        
        try:
            response = await self.call_gemini(prompt, max_tokens=2048)
            response = self._clean_json(response)
            
            # Try to parse JSON
            try:
                questions = json.loads(response)
            except json.JSONDecodeError as je:
                logger.error(f"JSON parse error: {je}. Response: {response[:200]}")
                # Return fallback questions when JSON parsing fails
                return self._create_fallback_questions(topic_name, num_questions, difficulty)
            
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
            
            # If no valid questions extracted, use fallback
            if not validated_questions:
                logger.warning(f"No valid questions extracted from quiz generation, using fallback")
                questions = self._create_fallback_questions(topic_name, num_questions, difficulty)
            else:
                questions = validated_questions[:num_questions]
            
            # Hide correct answers if not requested (practice mode)
            if not include_correct_answer:
                for q in questions:
                    q.pop("correctAnswer", None)
                    q.pop("correctIdx", None)
            
            return questions
        
        except Exception as e:
            logger.error(f"Error generating quiz: {e}")
            # Return fallback questions based on topic
            return self._create_fallback_questions(topic_name, num_questions, difficulty)
    
    def _create_fallback_questions(
        self, 
        topic: str, 
        count: int,
        difficulty: str = "mixed"
    ) -> List[Dict[str, Any]]:
        """Create high-quality fallback questions when AI APIs fail. Generates unique variations automatically."""
        
        # Extended question bank for better variation
        fallback_questions = {
            "python": [
                {"q": "What is the correct syntax for defining a function in Python?", "opts": ["func name():", "def name():", "function name():", "define name():"], "ans": 1},
                {"q": "Which of the following is a mutable data type in Python?", "opts": ["tuple", "string", "list", "frozenset"], "ans": 2},
                {"q": "What does the len() function return for a string?", "opts": ["First character", "Last character", "Number of characters", "ASCII value"], "ans": 2},
                {"q": "How do you create a dictionary in Python?", "opts": ["dict = []", "dict = {}", "dict = ()", "dict = <>"], "ans": 1},
                {"q": "What is the output of print(3 ** 2)?", "opts": ["6", "9", "5", "1"], "ans": 1},
                {"q": "Which keyword is used to create a loop in Python?", "opts": ["loop", "while", "iterate", "repeat"], "ans": 1},
                {"q": "What is the correct way to comment a single line in Python?", "opts": ["// comment", "/* comment */", "# comment", "-- comment"], "ans": 2},
                {"q": "How do you access the first element of a list?", "opts": ["list[1]", "list(0)", "list[0]", "list.first()"], "ans": 2},
                {"q": "What keyword is used to import modules in Python?", "opts": ["include", "import", "require", "load"], "ans": 1},
                {"q": "Which data type is used for storing true/false values?", "opts": ["bool", "boolean", "bit", "flag"], "ans": 0},
                {"q": "How do you check the type of a variable in Python?", "opts": ["check_type()", "typeof()", "type()", "getType()"], "ans": 2},
                {"q": "What is the result of 'hello' + 'world' in Python?", "opts": ["error", "helloworld", "hello world", "None"], "ans": 1},
                {"q": "Which method converts a string to lowercase?", "opts": ["lowercase()", "lower()", "toLower()", "tolowercase()"], "ans": 1},
                {"q": "What is the output of range(5)?", "opts": ["0-5", "1,2,3,4,5", "0,1,2,3,4", "5"], "ans": 2},
            ],
            "java": [
                {"q": "What does JVM stand for?", "opts": ["Java Virtual Machine", "Java Version Manager", "Java Verified Module", "Java Valid Method"], "ans": 0},
                {"q": "Which is the correct syntax for array declaration in Java?", "opts": ["int[] arr;", "int arr[];", "Both A and B", "int array[];"], "ans": 2},
                {"q": "What is the default value of a boolean variable in Java?", "opts": ["true", "false", "0", "null"], "ans": 1},
                {"q": "How do you create a new object in Java?", "opts": ["new", "create", "object", "make"], "ans": 0},
                {"q": "What is the superclass of all classes in Java?", "opts": ["Parent", "SuperClass", "Object", "Class"], "ans": 2},
                {"q": "Which keyword is used to prevent inheritance in Java?", "opts": ["protected", "private", "final", "static"], "ans": 2},
                {"q": "What is the correct syntax for exception handling?", "opts": ["try-catch", "catch-try", "attempt-error", "test-fail"], "ans": 0},
                {"q": "How do you declare a constant integer in Java?", "opts": ["constant int x = 5;", "final int x = 5;", "static int x = 5;", "immutable int x = 5;"], "ans": 1},
                {"q": "Which keyword makes a class impossible to extend?", "opts": ["sealed", "final", "abstract", "interface"], "ans": 1},
                {"q": "What is a constructor in Java?", "opts": ["A regular method", "A special method for object initialization", "A static method", "A deprecated method"], "ans": 1},
                {"q": "Which method is automatically called when object is created?", "opts": ["main()", "init()", "constructor()", "<constructor name>()"], "ans": 3},
                {"q": "What is the scope of 'static' keyword in Java?", "opts": ["Instance level", "Class level", "Method level", "Local level"], "ans": 1},
                {"q": "Which interface must be implemented for custom objects comparison?", "opts": ["Comparable", "Iterator", "Cloneable", "Serializable"], "ans": 0},
                {"q": "What does 'this' keyword refer to in Java?", "opts": ["Current method", "Current class", "Current object", "Parent class"], "ans": 2},
            ],
            "javascript": [
                {"q": "What does DOM stand for?", "opts": ["Data Object Model", "Document Object Model", "Digital Object Module", "Dynamic Object Manifest"], "ans": 1},
                {"q": "How do you declare a variable in JavaScript?", "opts": ["variable x = 5;", "var x = 5;", "declare x = 5;", "new x = 5;"], "ans": 1},
                {"q": "What is the correct way to write a comment in JavaScript?", "opts": ["# comment", "// comment", "-- comment", "/* comment"], "ans": 1},
                {"q": "How do you create an arrow function?", "opts": ["function => {}", "=> function {}", "() => {}", "-> function {}"], "ans": 2},
                {"q": "What is the result of typeof null?", "opts": ["\"null\"", "\"object\"", "\"undefined\"", "null"], "ans": 1},
                {"q": "How do you access an object property?", "opts": ["object.property", "object[property]", "Both A and B", "object->property"], "ans": 2},
                {"q": "What does async/await do in JavaScript?", "opts": ["Waits for download", "Handles asynchronous operations", "Sleeps the function", "Repeats code"], "ans": 1},
                {"q": "How do you parse a string to an integer?", "opts": ["parseInt()", "parseFloat()", "Number()", "Both A and C"], "ans": 3},
                {"q": "What is the difference between let and var?", "opts": ["No difference", "let is block-scoped, var is function-scoped", "var is faster", "let is older"], "ans": 1},
                {"q": "How do you create an object in JavaScript?", "opts": ["new Object()", "Object literals {}", "Both A and B", "constructor() {}"], "ans": 2},
                {"q": "What does the spread operator (...) do?", "opts": ["Adds numbers", "Expands iterables", "Creates a copy", "Removes items"], "ans": 1},
                {"q": "How do you fetch data from an API?", "opts": ["ajax()", "fetch()", "request()", "http()"], "ans": 1},
                {"q": "What is a Promise in JavaScript?", "opts": ["A function call", "An object for async operations", "A variable type", "A loop"], "ans": 1},
                {"q": "How do you prevent default form submission?", "opts": ["preventDefault()", "stopDefault()", "cancelEvent()", "blockSubmit()"], "ans": 0},
            ],
            "html": [
                {"q": "What does HTML stand for?", "opts": ["Hyper Text Markup Language", "HTML Text Markup Language", "Home Tool Markup Language", "Hyperlinks and Text Markup Language"], "ans": 0},
                {"q": "Which tag is used for the largest heading?", "opts": ["<h1>", "<h6>", "<head>", "<header>"], "ans": 0},
                {"q": "What is the correct syntax for an unordered list?", "opts": ["<ul><li>", "<ol><li>", "<list>", "<ul><item>"], "ans": 0},
                {"q": "Which attribute specifies an alternative text for an image?", "opts": ["alt", "src", "title", "description"], "ans": 0},
                {"q": "What does <meta> tag define?", "opts": ["Metadata about HTML", "Main content", "Meta information for CSS", "Metadata file"], "ans": 0},
                {"q": "How do you insert a comment in HTML?", "opts": ["<!-- comment -->", "// comment", "# comment", "/* comment */"], "ans": 0},
                {"q": "Which tag is used to define a paragraph?", "opts": ["<p>", "<paragraph>", "<text>", "<para>"], "ans": 0},
                {"q": "What is the correct way to link to an external CSS file?", "opts": ["<link rel=\"stylesheet\" href=\"style.css\">", "<style src=\"style.css\">", "<css href=\"style.css\">", "<import=\"style.css\">"], "ans": 0},
            ],
        }
        
        # Find questions for this topic (case-insensitive)
        topic_lower = topic.lower().strip()
        questions_pool = fallback_questions.get(topic_lower, [])
        
        # If no specific pool, create contextual questions for any topic
        if not questions_pool:
            questions_pool = [
                {"q": f"What is the primary goal of {topic}?", "opts": ["To establish foundational knowledge", "To provide advanced techniques", "To enforce best practices", "To build practical skills"], "ans": 3},
                {"q": f"Why is {topic} important in programming?", "opts": ["It's optional for most projects", "It improves code quality and maintainability", "It's only used in enterprise applications", "It's legacy technology"], "ans": 1},
                {"q": f"What is a common pitfall when learning {topic}?", "opts": ["Moving too fast without practice", "Focusing too much on theory", "Not applying concepts to real projects", "All of the above"], "ans": 3},
                {"q": f"How should you approach mastering {topic}?", "opts": ["By memorizing definitions", "By understanding concepts and practicing regularly", "By reading documentation once", "By copying code from examples"], "ans": 1},
                {"q": f"What does proficiency in {topic} require?", "opts": ["Quick memorization only", "Consistent practice and problem-solving", "Understanding theory without implementation", "Following tutorials passively"], "ans": 1},
                {"q": f"Which best describes effective learning of {topic}?", "opts": ["Passive reading of materials", "Active practice with projects and exercises", "Studying others' code exclusively", "Avoiding mistakes entirely"], "ans": 1},
                {"q": f"What's the relationship between {topic} and real-world applications?", "opts": ["It's rarely used in practice", "It's fundamental to professional development", "It's only for academic purposes", "It applies only to legacy systems"], "ans": 1},
                {"q": f"How can you verify your understanding of {topic}?", "opts": ["By passing quizzes alone", "By implementing projects and solving problems", "By reading about it", "By discussing it theoretically"], "ans": 1},
                {"q": f"What is essential for becoming proficient in {topic}?", "opts": ["Hours of theory", "Consistent practice and real-world application", "Memorizing syntax", "Following a single resource"], "ans": 1},
                {"q": f"When learning {topic}, what should be your focus?", "opts": ["Understanding concepts first, then coding", "Coding without understanding concepts", "Memorizing code patterns", "Avoiding practice problems"], "ans": 0},
            ]
        
        # Build result with question variation
        result = []
        import random
        
        # Get questions and handle cases where more questions are requested than available
        pool_size = len(questions_pool)
        
        for i in range(count):
            # Use modulo to cycle through questions without repetition and randomize order
            idx = (i + random.randint(0, min(5, pool_size-1))) % pool_size
            q_data = questions_pool[idx]
            
            # Create variations of question by slightly modifying question text
            question_variation = q_data["q"]
            if i >= pool_size:
                # Add variation for questions beyond pool size
                variations = [
                    f"[Variant] {q_data['q']}",
                    f"According to best practices, {q_data['q'][0].lower()}{q_data['q'][1:]}",
                    f"In the context of {topic}, {q_data['q'][0].lower()}{q_data['q'][1:]}",
                ]
                question_variation = variations[(i // pool_size) % len(variations)]
            
            result.append({
                "id": f"fallback_q{i+1}",
                "question": question_variation,
                "options": q_data["opts"][:],  # Create new list to avoid reference issues
                "correctAnswer": q_data["ans"],
                "correctIdx": q_data["ans"],
                "explanation": f"This question tests your understanding of {topic}. Correct answer: {chr(65 + q_data['ans'])}",
                "difficulty": difficulty if difficulty != "mixed" else ["easy", "medium", "hard"][i % 3],
                "type": "mcq",
                "isFallback": True
            })
        
        logger.info(f"⏭️  Using {len(result)} fallback questions for topic: {topic} (pool size: {pool_size})")
        return result
    
    async def generate_mock_test(
        self,
        topics: List[str],
        total_questions: int = 20,
        difficulty_mix: Optional[Dict[str, int]] = None,
        history: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive mock test"""
        
        programming_language = ", ".join(topics)
        n = total_questions
        
        # Calculate distribution: ~50% MCQ, 25% Fillups, 25% Descriptive
        n1 = n // 2
        n2 = n // 4
        n3 = n - n1 - n2
        
        history_str = ""
        if history:
            history_str = f"\n\nCRITICAL: DO NOT repeat or generate any of these previous questions:\n" + "\n".join([f"- {h}" for h in history])

        prompt = f"""You are a mock test generator. Generate a unique, non-repetitive test based on the following:{history_str}

**Language/Topic:** {programming_language}
**Total Questions:** {n}
**Distribution:**
- MCQ: {n1} questions (4 options each, only one correct)
- Fill in the Blanks: {n2} questions
- Answer the Following: {n3} questions

**STRICT RULES - You MUST follow these:**
1. ANTI-REPEAT SYSTEM: Maintain a running list of ALL questions asked in this entire conversation.
2. If a similar question (same concept, same answer, or same wording) was already asked — SKIP it and generate a different one.
3. NEVER repeat the same question, concept, or answer from any previous test.
4. Each question must test a DIFFERENT sub-topic or concept. Do not ask about the same function, keyword, or concept twice.
5. If all easy questions on a topic are exhausted, move to medium/hard variants.
6. Treat each question as UNIQUE by tracking: topic + concept + correct answer combination.
7. Cover a WIDE range of topics from the language — do NOT cluster around one area.
8. Before generating, mentally list 30 distinct sub-topics of {programming_language} and pick from different ones for each question.

**PREVIOUS QUESTIONS (MUST NOT REPEAT):**
{history_str}

**Output Format:**
Return ONLY valid JSON in this exact structure:
{{
  "mcq": [
    {{
      "question": "...",
      "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
      "answer": "A"
    }}
  ],
  "fillups": [
    {{
      "question": "The ___ function is used to ...",
      "answer": "..."
    }}
  ],
  "descriptive": [
    {{
      "question": "...",
      "answer": "..."
    }}
  ]
}}"""
        
        try:
            response = await self.call_gemini(prompt, max_tokens=3000)
            response = self._clean_json(response)
            test_data = json.loads(response)
            
            # Ensure we have the right structure based on new prompt formula
            if "mcq" in test_data:
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
        weak_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
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