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
                f"You are EduTwin AI, a friendly and knowledgeable learning tutor. Student name: {user_name}. "
                "Your mission: Help students learn and understand concepts deeply through clear, structured explanations. "
                "Be warm, encouraging, and use simple language. For learning topics, provide thorough, accurate explanations."
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

GEN Z SLANG TRANSLATION GUIDE (FOR UNDERSTANDING ONLY):
Understand these terms but respond professionally:
- "no cap" / "facts" / "fax" = That's true / Agreed / Really?
- "slay" / "ate" / "bussin" = Great job / That's awesome / That's really good
- "mid" / "trash" = Not good / Mediocre
- "lowkey" / "highkey" = Sort of / Really
- "it's giving" / "it's giving off" = It seems like / It looks like
- "dope" / "lit" / "fire" = Cool / Awesome
- "vibe" / "vibes" = Feeling / Mood
- "bet" = Okay / Understood / Sure
- "periodt" / "point blank" = That's final / No more debate
- "salty" = Upset / Bitter
- "flex" = Show off
- "sus" / "sus behavior" = Suspicious / Seems off
- "fr fr" / "for real" = For real / Seriously
- "ngl" = Not gonna lie
- "idk" / "idek" = I don't know / I don't even know
- "nah" = No
- "ong" / "on god" = On god / For real
- "deadass" = Seriously / For real
- "no lie" = Honestly / For real
- "that slaps" = That's really good / I like it
- "ate and left no crumbs" = Did excellently
- "unhinged" = Funny / Chaotic in a good way
- "it's not serious" / "valid" = Acceptable / Makes sense

INTERACTION GUIDELINES (CRITICAL):
✅ DO THIS:
- Be warm, friendly, and encouraging always
- UNDERSTAND Gen Z vocabulary but respond using clear, professional language
- If user uses slang, decode it to the actual question and answer clearly
- Don't judge or lecture about slang usage - just understand and help
- Give complete, detailed explanations that help learners truly understand
- For greetings: Respond warmly and invite learning questions
- For learning questions: Provide thorough, well-structured answers with examples
- For out-of-topic questions: Say "I'm your AI tutor and I'm here for training you. Let's learn something new today!" then suggest a relevant topic
- Show you understand their casual style by being relatable but still professional in YOUR response

PROGRESSIVE LEARNING APPROACH (IMPORTANT):
- If user asks about Python GENERALLY (like "explain Python" or "what is Python"):
  * FIRST: Define Python clearly (what it is, why it's useful)
  * THEN: Ask specifically which Python topic they want to learn
  * THEN: List 6-8 beginner-friendly Python topics to choose from
  * DON'T jump straight to detailed explanation without asking
  
- If user asks about a SPECIFIC Python topic (like "explain for loops" or "what are variables"):
  * DIRECTLY provide DETAILED explanation with multiple examples
  * Follow the structured format exactly
  * Go deep into the topic

- Examples of GENERAL Python questions: "What is Python?", "Tell me about Python", "Python basics", "Explain Python"
- Examples of SPECIFIC Python topics: "for loops", "functions", "lists", "dictionaries", "variables", "classes", "recursion"

❌ DON'T DO THIS:
- Be cold or dismissive
- Give vague or incomplete explanations
- Use "Sorry, I can only answer questions related to the provided learning topics."
- Lecture the user about their slang
- Use forced Gen Z slang in responses (be naturally friendly instead)
- Pretend you don't understand slang
- When user says "Python" generally, immediately jump into detailed topic explanation without asking what they want

EXAMPLES OF GEN Z TO PROFESSIONAL TRANSLATION:

User says: "Yo, explain Python for loops no cap 🔥🔥 that would be bussin"
You understand as: "Please explain Python for loops properly. I think that would be really helpful."
You respond with: Regular professional structured response, understanding their enthusiasm

User says: "Nah this recursion thing is lowkey sus fr fr"
You understand as: "I find recursion somewhat confusing or suspicious / unclear."
You respond with: Clear breakdown of recursion explaining why it might seem confusing

User says: "bet, can you help me debug this code deadass"
You understand as: "Sure, please help me debug this code seriously."
You respond with: Structured debugging help with examples

EXAMPLE - PROGRESSIVE LEARNING FOR GENERAL PYTHON:
User says: "explain python"
You respond with:
### 📚 What is Python?
[Define Python in 2-3 sentences]

### 🎯 Why Python is Awesome
- Point 1: Easy to learn
- Point 2: Powerful
- etc.

### 💡 Popular Uses
- Web development
- Data science
- Automation
- AI/Machine Learning

### 🚀 Which Python Topic Would You Like to Learn?
Pick one of these beginner-friendly topics:
1. **Variables & Data Types** - Store and work with information
2. **If/Else Statements** - Make decisions in code
3. **For Loops** - Repeat code multiple times
4. **While Loops** - Repeat until something happens
5. **Functions** - Organize reusable code
6. **Lists** - Work with multiple items
7. **Dictionaries** - Organize data with labels
8. **String Operations** - Work with text

What sounds interesting to you? Just say the number or the topic name!

EXAMPLE - DETAILED EXPLANATION FOR SPECIFIC TOPIC:
User says: "I want to learn for loops" (after seeing the list above)
OR User says directly: "explain for loops"
You respond with FULL DETAILED explanation following the structured format.

RESPONSE STRUCTURE (MUST FOLLOW EXACTLY):

For GENERAL/INTRO Questions (like "What is Python?"):
### 📚 [Topic Name]
1-2 sentences explaining what it is

### 🎯 Key Benefits/Points
- Point 1
- Point 2
- Point 3+

### 💡 Common Uses/Examples
- Use case 1
- Use case 2

### 🚀 What Would You Like to Learn?
List specific topics with brief descriptions,
OR ask which specific subtopic they want to dive into

For SPECIFIC/DETAILED Questions (like "explain for loops"):
### 📚 Quick Answer
1-2 sentences directly answering their question.

### 🎯 Key Points
- Point 1: Clear and concise
- Point 2: Builds on point 1
- Point 3-5: Additional insights (3-5 total)

### 💡 Example
Show code example or scenario with 2-3 line explanation.

### 🚀 Next Step
One practical action + one follow-up question.

For Greetings:
Just one warm, welcoming sentence and ask what they'd like to learn!

For Out-of-Topic:
"I'm your AI tutor and I'm here for training you. Let's learn something new today! How about we explore [suggest topic]?"

CRITICAL RULES:
- Explanations must be COMPLETE and CORRECT
- Always structure properly with markdown
- Be encouraging and supportive
- No harsh rejections ever
- Understand casual/slang language but respond professionally
- Never be condescending about language choices
- If follow-up: Do NOT repeat greetings
- Never re-introduce yourself after first turn
- For general topics: Ask and guide, don't assume
- For specific topics: Provide detailed explanation immediately

### 🎯 Key Points
- Point 1: Clear and concise
- Point 2: Builds on point 1
- Point 3-5: Additional insights (3-5 total)

### 💡 Example
Show code example or scenario with 2-3 line explanation.

### 🚀 Next Step
One practical action + one follow-up question.

For Greetings:
Just one warm, welcoming sentence and ask what they'd like to learn!

For Out-of-Topic:
"I'm your AI tutor and I'm here for training you. Let's learn something new today! How about we explore [suggest topic]?"

CRITICAL RULES:
- Explanations must be COMPLETE and CORRECT
- Always structure properly with markdown
- Be encouraging and supportive
- No harsh rejections ever
- Understand casual/slang language but respond professionally
- Never be condescending about language choices
- If follow-up: Do NOT repeat greetings
- Never re-introduce yourself after first turn"""
            
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
        
        # Specific Python topics - provide detailed explanation
        specific_topics = {
            "for loop": """### 📚 Quick Answer
**For Loop** iterates over each item in a sequence, running code for each item.

### 🎯 Key Points
- Use `for` loop when you know what you're looping through (list, string, range)
- Each iteration processes one item at a time
- Much cleaner than while loops for collections
- The loop variable updates automatically after each iteration
- No risk of infinite loops if you use it correctly

### 💡 Example
```python
for i in range(3):
    print(i)  # Prints: 0, 1, 2

for name in ["Alice", "Bob", "Charlie"]:
    print(f"Hello, {name}")
```
The first example loops 3 times. The second loops through a list of names.

### 🚀 Next Step
Try writing a for loop that prints numbers 1 to 5, or loops through your favorite items. What will you loop through?""",
            
            "while loop": """### 📚 Quick Answer
**While Loop** repeats code as long as a condition is true. Once the condition becomes false, the loop stops.

### 🎯 Key Points
- Use `while` when repeat count is unknown (reading until "quit", games, etc.)
- Must update the condition variable inside the loop
- Missing the update causes infinite loops (very bad!)
- Check condition BEFORE each iteration
- More dangerous than `for` loops if not careful

### 💡 Example
```python
count = 0
while count < 3:
    print(f"Count: {count}")
    count += 1  # MUST DO THIS or infinite loop!

# User input example
user_input = ""
while user_input != "quit":
    user_input = input("Type 'quit' to exit: ")
    print(f"You said: {user_input}")
```

### 🚀 Next Step
Try writing a while loop that counts down from 5 to 1, or asks user for input until they say "done". Remember to update the condition!""",
            
            "variables": """### 📚 Quick Answer
**Variables** are named containers that store information (numbers, text, true/false, etc.) for your program to use.

### 🎯 Key Points
- Variables give names to data so you can reuse them
- Names should be descriptive (age, name, total_score, not x or y)
- Python figures out the data type automatically
- You can change a variable's value anytime
- Use snake_case for variable names in Python (my_variable, not myVariable)

### 💡 Example
```python
age = 15  # Integer (whole number)
name = "Alex"  # String (text)
is_student = True  # Boolean (true/false)
height = 5.8  # Float (decimal number)

print(f"{name} is {age} years old")  # Reuse variables
age = 16  # Change the value
print(age)  # Now prints 16, not 15
```

### 🚀 Next Step
Create 3 variables about yourself: your name, age, and favorite hobby. Then print them like "My name is [name], I'm [age], and I love [hobby].".""",
            
            "function": """### 📚 Quick Answer
**Functions** are reusable blocks of code that perform specific tasks. Define once, use many times!

### 🎯 Key Points
- Functions reduce code repetition (DRY: Don't Repeat Yourself)
- Define with `def`, call with function_name()
- Can accept inputs (parameters) and return outputs
- Parameters are like variables that functions receive
- Return sends data back to whoever called the function

### 💡 Example
```python
def greet(name):
    return f"Hello, {name}! Welcome to learning! 🎓"

message = greet("Alex")  # Call function
print(message)  # Prints: Hello, Alex! Welcome to learning! 🎓

def add_numbers(a, b):
    return a + b

result = add_numbers(5, 3)
print(result)  # Prints: 8
```

### 🚀 Next Step
Write a function that takes two numbers and returns their product (multiply). Call it with different numbers!""",
            
            "list": """### 📚 Quick Answer
**Lists** store multiple items in one variable. Think of it like a shopping list where each item has a position.

### 🎯 Key Points
- Lists use square brackets: [item1, item2, item3]
- Access items by position (first item is position 0, not 1!)
- Lists can change: add, remove, or modify items
- Items can be any type: numbers, text, mixed, even other lists
- Use loops to go through all items quickly

### 💡 Example
```python
fruits = ["apple", "banana", "orange"]
print(fruits[0])  # Prints: apple (position 0 is first!)
print(fruits[2])  # Prints: orange (position 2 is third!)

fruits.append("mango")  # Add to end
fruits.remove("banana")  # Remove item
print(fruits)  # Prints: ['apple', 'orange', 'mango']

for fruit in fruits:  # Loop through
    print(fruit)
```

### 🚀 Next Step
Create a list of 5 things you want to learn. Add 2 more items to it and print each one.""",
            
            "dictionary": """### 📚 Quick Answer
**Dictionaries** store information as key-value pairs (like a real dictionary: word→meaning). Super organized!

### 🎯 Key Points
- Use curly braces: {key: value, key: value}
- Access by key, not position: my_dict["key"]
- Keys are usually text/strings, values can be anything
- Dictionaries are great for structured data
- Much more readable than lists for labeled data

### 💡 Example
```python
student = {
    "name": "Alex",
    "age": 15,
    "grade": "10th",
    "favorite_subject": "Computer Science"
}

print(student["name"])  # Prints: Alex
print(student["age"])   # Prints: 15

student["age"] = 16  # Update value
student["school"] = "Tech High"  # Add new key-value

for key in student:  # Loop through
    print(f"{key}: {student[key]}")
```

### 🚀 Next Step
Create a dictionary about yourself with: name, hobby, favorite_book, lucky_number. Print each value!"""
        }
        
        # Check for specific topics first
        for topic, response in specific_topics.items():
            if topic in lower_msg:
                return response
        
        # General Python question - use progressive learning approach
        if "python" in lower_msg and "for loop" not in lower_msg and "while loop" not in lower_msg:
            # Check if it's asking for general Python or general programming
            general_python_phrases = ["what is python", "explain python", "about python", "python basics", 
                                     "introduce python", "get started python", "learn python", "python tutorial",
                                     "python beginners"]
            
            is_general_question = any(phrase in lower_msg for phrase in general_python_phrases)
            
            if is_general_question:
                # PROGRESSIVE LEARNING: Ask what they want to learn
                return f"""### 📚 What is Python?
Python is a beginner-friendly, powerful programming language used for everything - websites, apps, data science, AI, automation, and more!

### 🎯 Why Python is Awesome
- **Easy to Learn**: Reads almost like English
- **Powerful**: Can build real projects fast
- **Huge Community**: Tons of libraries and help available
- **In-Demand**: Companies love Python developers
- **Versatile**: Works for web, data, AI, scripting, and more

### 💡 Popular Uses
- 🌐 Web apps and servers (Instagram, Spotify use it)
- 📊 Data analysis and visualization
- 🤖 Artificial Intelligence and Machine Learning
- 🔧 Automation and scripting
- 🎮 Game development
- 💻 Desktop applications

### 🚀 What Python Topic Would You Like to Learn First?

Pick one that interests you (or just type the number or name):

1. **Variables** - Store and work with information
2. **Data Types** - Numbers, text, true/false  
3. **If/Else** - Make decisions in code
4. **While Loops** - Repeat until something happens
5. **For Loops** - Repeat for each item
6. **Functions** - Create reusable code
7. **Lists** - Work with multiple items
8. **Dictionaries** - Organize data with labels

💡 **Pro Tip**: Start with Variables and If/Else, then move to loops!

Which topic sounds good to you? Just say the number or topic name, and I'll explain it in detail! 🚀"""
            else:
                # They mentioned Python but with a specific context
                return f"""### 📚 Quick Answer
I'm your AI tutor! 🎓 I can explain Python, help debug code, and guide you through programming concepts with real examples.

### 🎯 Popular Python Topics
- Variables & data types
- If/Else statements
- Loops (for & while)
- Functions
- Lists and dictionaries
- String operations
- File handling
- Object-oriented programming

### 💡 I Can Help You With
- Learning new concepts with examples
- Fixing bugs in your code
- Understanding error messages
- Writing better code
- Building projects step-by-step

### 🚀 Next Step
Tell me specifically what you want to learn:
- "What are variables?"
- "Explain for loops"
- "Help me debug this code"
- "Show me how to use lists"

Let's make learning fun! 💪"""
        
        elif "programming" in lower_msg:
            return f"""### 📚 Quick Answer
I'm your AI tutor! 🎓 I specialize in programming and can help you learn any language or concept.

### 🎯 Languages I Can Help With
- **Python** - Best for beginners, data science, automation
- **JavaScript** - For web and interactive apps
- **Java** - For big systems and Android apps
- **C++** - For performance and games
- **SQL** - For databases

### 💡 Topics I Cover
✨ Variables, data types, operators
🔄 Loops and conditionals
📦 Functions and modules
📋 Arrays and data structures
🔗 Object-oriented programming
🐛 Debugging and problem-solving
💾 File handling and databases

### 🚀 What Language or Topic Interests You?
Just ask and I'll explain it with clear examples and code! 🚀"""
        
        else:
            return f"""### 📚 Quick Answer
I'm your AI tutor and I'm here for training you. Let's learn something new today! 🎓

### 🎯 Key Points
- I specialize in programming and computer science
- I explain concepts clearly with real-world examples
- I help you understand, not just memorize
- Every question gets a structured, detailed answer
- I support multiple languages and learning styles

### 💡 What I Can Help With
✨ **Programming**: Python, JavaScript, Java, C++, etc.
🐛 **Debugging**: Fix errors and understand why they happen
💡 **Algorithms**: Learn problem-solving techniques
📝 **Practice**: Get quiz questions and practice problems
📚 **Concepts**: Understand complex ideas simply

### 🚀 Next Step
Ask me something specific about what you want to learn:
- "What is Python?"
- "Explain for loops"
- "What's recursion?"
- "How do I write a function?"
- "Explain arrays vs linked lists"

I'm excited to help you learn! 🚀 What topic interests you?"""

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