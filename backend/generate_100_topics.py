"""
Generate 100 programming topics (10 languages x 10 topics) using Gemini API + YouTube API.

Each topic includes:
 - Rich overview
 - 4 explanation styles (simplified, logical, visual, analogy) with code examples
 - 10 quiz questions (MCQ) with real questions
 - YouTube video recommendations
 - Subtopics with full content

Run:  python generate_100_topics.py
"""

import json, time, sys, os, re, asyncio, logging
import pymongo, httpx
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DB_NAME = "pixel_pirates"

# ── 100 Topics: 10 languages x 10 topics ──────────────────────────
TOPIC_DEFS = [
    # Python (1-10)
    ("Python", "History & Philosophy", "Beginner", "Guido van Rossum, Zen of Python, PEP 8, design philosophy, interpreted language, dynamic typing, Python 2 vs 3"),
    ("Python", "Syntax & Basics", "Beginner", "variables, data types, operators, input/output, indentation, comments, type conversion"),
    ("Python", "Control Structures", "Beginner", "if/elif/else, for loops, while loops, break, continue, pass, range(), nested loops"),
    ("Python", "Functions & Recursion", "Intermediate", "def, return, parameters, *args, **kwargs, lambda, recursion, base case, memoization"),
    ("Python", "Data Structures", "Intermediate", "lists, dictionaries, sets, tuples, list comprehension, dict methods, set operations"),
    ("Python", "OOP - Classes & Inheritance", "Intermediate", "classes, __init__, self, inheritance, super(), polymorphism, encapsulation, dunder methods"),
    ("Python", "Advanced Features", "Advanced", "decorators, generators, async/await, context managers, metaclasses, closures"),
    ("Python", "Libraries - NumPy, Pandas, Flask", "Intermediate", "NumPy arrays, Pandas DataFrame, Flask routes, data manipulation, web development"),
    ("Python", "File Handling & Databases", "Intermediate", "open, read, write, CSV, JSON, SQLite, with statement, CRUD operations"),
    ("Python", "Applications - AI/ML & Web Dev", "Advanced", "machine learning basics, TensorFlow, scikit-learn, web scraping, automation, Django/Flask"),

    # JavaScript (11-20)
    ("JavaScript", "History & ECMAScript", "Beginner", "Brendan Eich, ES6+, TC39, browser wars, Node.js history, ECMAScript standards"),
    ("JavaScript", "Syntax & Basics (ES6+)", "Beginner", "let, const, var, data types, operators, template literals, type coercion, strict mode"),
    ("JavaScript", "Control Structures", "Beginner", "if/else, switch, for, while, for...of, for...in, break, continue, ternary operator"),
    ("JavaScript", "Functions & Closures", "Intermediate", "function declarations, arrow functions, closures, IIFE, callbacks, higher-order functions, this binding"),
    ("JavaScript", "Data Structures", "Intermediate", "arrays, objects, Map, Set, WeakMap, destructuring, spread/rest operators, JSON"),
    ("JavaScript", "OOP - Prototypes & Classes", "Intermediate", "prototypes, prototype chain, ES6 classes, constructor, extends, super, static methods"),
    ("JavaScript", "Advanced Features", "Advanced", "async/await, Promises, event loop, generators, Proxy, Reflect, Symbol, iterators"),
    ("JavaScript", "Libraries - React & Node.js", "Intermediate", "React components, JSX, hooks, useState, useEffect, Node.js, Express.js, npm"),
    ("JavaScript", "File Handling & APIs", "Intermediate", "Fetch API, JSON parsing, REST APIs, localStorage, File API, FormData, CORS"),
    ("JavaScript", "Applications - Web & Mobile", "Advanced", "SPA, PWA, React Native, Electron, serverless, WebSocket, service workers"),

    # C (21-30)
    ("C", "History & Basics", "Beginner", "Dennis Ritchie, UNIX, compiled language, gcc, hello world, structured programming"),
    ("C", "Syntax & Data Types", "Beginner", "int, float, double, char, sizeof, typedef, constants, format specifiers, scanf/printf"),
    ("C", "Control Structures", "Beginner", "if/else, switch, for, while, do-while, break, continue, goto, nested loops"),
    ("C", "Functions & Pointers", "Intermediate", "function prototypes, pass-by-value, pass-by-reference, pointers, dereferencing, pointer arithmetic, function pointers"),
    ("C", "Arrays & Strings", "Intermediate", "array declaration, multidimensional arrays, string functions, strlen, strcpy, strcmp, char arrays"),
    ("C", "Structures & Unions", "Intermediate", "struct, union, typedef, nested structs, bit fields, enum, size comparison"),
    ("C", "Memory Management", "Advanced", "malloc, calloc, realloc, free, memory leaks, dangling pointers, stack vs heap"),
    ("C", "File Handling", "Intermediate", "fopen, fclose, fread, fwrite, fprintf, fscanf, binary files, file modes"),
    ("C", "Standard Libraries", "Intermediate", "stdio.h, stdlib.h, string.h, math.h, ctype.h, time.h, assert.h"),
    ("C", "Applications - Systems Programming", "Advanced", "operating systems, embedded systems, device drivers, kernel modules, real-time systems"),

    # C++ (31-40)
    ("C++", "History & Basics", "Beginner", "Bjarne Stroustrup, C with classes, ISO standards, C++11/14/17/20, compilation process"),
    ("C++", "Syntax & Data Types", "Beginner", "variables, auto, references, const, constexpr, namespaces, iostream, type casting"),
    ("C++", "Control Structures", "Beginner", "if/else, switch, for, while, range-based for, break, continue, structured bindings"),
    ("C++", "Functions & Templates", "Intermediate", "function overloading, default parameters, inline, templates, function templates, template specialization"),
    ("C++", "STL Data Structures", "Intermediate", "vector, list, map, set, unordered_map, stack, queue, deque, priority_queue, iterators"),
    ("C++", "OOP - Classes & Polymorphism", "Intermediate", "classes, constructors, destructors, inheritance, virtual functions, abstract classes, multiple inheritance"),
    ("C++", "Advanced Features", "Advanced", "operator overloading, smart pointers, move semantics, RAII, lambda expressions, exception handling"),
    ("C++", "Libraries - STL & Boost", "Intermediate", "algorithm header, sort, find, transform, Boost library, OpenCV basics, Qt basics"),
    ("C++", "File Handling & Streams", "Intermediate", "ifstream, ofstream, fstream, stringstream, binary I/O, serialization"),
    ("C++", "Applications - Games & Systems", "Advanced", "game engines, Unreal Engine, OS development, compilers, high-performance computing"),

    # Java (41-50)
    ("Java", "History & Basics", "Beginner", "James Gosling, JVM, JRE, JDK, write once run anywhere, bytecode, garbage collection"),
    ("Java", "Syntax & Data Types", "Beginner", "primitive types, wrapper classes, String, arrays, type casting, operators, Scanner"),
    ("Java", "Control Structures", "Beginner", "if/else, switch, for, while, do-while, enhanced for, break, continue, labeled loops"),
    ("Java", "Functions & Methods", "Intermediate", "method declaration, parameters, return types, overloading, varargs, static methods, recursion"),
    ("Java", "Collections Framework", "Intermediate", "ArrayList, HashMap, HashSet, LinkedList, TreeMap, Queue, Iterator, Comparable, Comparator"),
    ("Java", "OOP - Classes & Interfaces", "Intermediate", "classes, inheritance, interfaces, abstract classes, polymorphism, encapsulation, packages"),
    ("Java", "Advanced Features", "Advanced", "generics, multithreading, lambda expressions, Stream API, Optional, annotations, reflection"),
    ("Java", "Frameworks - Spring & Hibernate", "Intermediate", "Spring Boot, dependency injection, REST APIs, Hibernate ORM, JPA, Maven/Gradle"),
    ("Java", "File Handling & JDBC", "Intermediate", "FileReader, BufferedReader, Files class, JDBC, PreparedStatement, ResultSet, try-with-resources"),
    ("Java", "Applications - Enterprise & Android", "Advanced", "enterprise applications, microservices, Android development, distributed systems, cloud deployment"),

    # HTML/CSS (51-60)
    ("HTML/CSS", "History & Basics", "Beginner", "Tim Berners-Lee, W3C, HTML5, CSS3, web standards, browser rendering, DOCTYPE"),
    ("HTML/CSS", "Elements & Attributes", "Beginner", "headings, paragraphs, links, images, lists, tables, div, span, id, class"),
    ("HTML/CSS", "Forms & Input", "Beginner", "form tag, input types, textarea, select, radio, checkbox, validation, submit"),
    ("HTML/CSS", "Semantic HTML", "Intermediate", "header, nav, main, section, article, aside, footer, figure, accessibility benefits"),
    ("HTML/CSS", "CSS Selectors & Properties", "Beginner", "element, class, id selectors, pseudo-classes, pseudo-elements, specificity, cascade"),
    ("HTML/CSS", "Layouts - Flexbox & Grid", "Intermediate", "flex container, justify-content, align-items, grid-template, fr units, gap, responsive layouts"),
    ("HTML/CSS", "Responsive Design", "Intermediate", "media queries, viewport meta, mobile-first, breakpoints, fluid grids, flexible images"),
    ("HTML/CSS", "Advanced CSS", "Advanced", "animations, transitions, transforms, keyframes, CSS variables, calc(), clamp()"),
    ("HTML/CSS", "Frameworks - Bootstrap & Tailwind", "Intermediate", "Bootstrap grid, components, Tailwind utility classes, customization, responsive modifiers"),
    ("HTML/CSS", "Applications - Web Design & UI/UX", "Advanced", "design principles, color theory, typography, accessibility, performance optimization, SEO"),

    # SQL (61-70)
    ("SQL", "History & Basics", "Beginner", "Edgar Codd, relational model, RDBMS, MySQL, PostgreSQL, SQL standards, database concepts"),
    ("SQL", "Data Types", "Beginner", "INT, VARCHAR, TEXT, DATE, DECIMAL, BOOLEAN, BLOB, NULL, type casting"),
    ("SQL", "DDL - CREATE, ALTER, DROP", "Intermediate", "CREATE TABLE, ALTER TABLE, DROP TABLE, constraints, PRIMARY KEY, FOREIGN KEY, AUTO_INCREMENT"),
    ("SQL", "DML - SELECT, INSERT, UPDATE, DELETE", "Beginner", "SELECT, FROM, WHERE, INSERT INTO, UPDATE SET, DELETE FROM, ORDER BY, LIMIT, DISTINCT"),
    ("SQL", "Joins & Subqueries", "Intermediate", "INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL JOIN, self join, subqueries, correlated subqueries, EXISTS"),
    ("SQL", "Constraints & Keys", "Intermediate", "PRIMARY KEY, FOREIGN KEY, UNIQUE, NOT NULL, CHECK, DEFAULT, composite keys, referential integrity"),
    ("SQL", "Views & Indexes", "Intermediate", "CREATE VIEW, indexed views, CREATE INDEX, B-tree, composite index, EXPLAIN, query optimization"),
    ("SQL", "Stored Procedures & Triggers", "Advanced", "CREATE PROCEDURE, parameters, cursors, triggers, BEFORE/AFTER, event handling"),
    ("SQL", "Transactions", "Intermediate", "BEGIN, COMMIT, ROLLBACK, ACID properties, isolation levels, deadlocks, savepoints"),
    ("SQL", "Applications - Databases & Analytics", "Advanced", "data warehousing, ETL, business intelligence, window functions, partitioning, performance tuning"),

    # TypeScript (71-80)
    ("TypeScript", "History & Basics", "Beginner", "Microsoft, Anders Hejlsberg, superset of JavaScript, type safety, compilation, tsconfig"),
    ("TypeScript", "Syntax & Types", "Beginner", "string, number, boolean, any, unknown, void, never, type inference, type assertions"),
    ("TypeScript", "Control Structures", "Beginner", "if/else, switch, for, while, for...of, type narrowing, type guards, discriminated unions"),
    ("TypeScript", "Functions", "Intermediate", "typed parameters, return types, optional parameters, overloads, generic functions, rest parameters"),
    ("TypeScript", "Interfaces & Generics", "Intermediate", "interface declaration, extending interfaces, generics, constraints, utility types, mapped types"),
    ("TypeScript", "OOP - Classes & Inheritance", "Intermediate", "classes, access modifiers, abstract classes, implements, readonly, parameter properties"),
    ("TypeScript", "Advanced Features", "Advanced", "decorators, namespaces, declaration merging, conditional types, template literal types, infer"),
    ("TypeScript", "Frameworks - Angular & NestJS", "Intermediate", "Angular components, dependency injection, NestJS controllers, modules, decorators, middleware"),
    ("TypeScript", "Compilation & Tooling", "Intermediate", "tsc, tsconfig.json, strict mode, source maps, declaration files, webpack integration"),
    ("TypeScript", "Applications - Large Scale Web", "Advanced", "monorepos, design patterns, type-safe APIs, Zod, tRPC, full-stack TypeScript"),

    # Kotlin (81-90)
    ("Kotlin", "History & Basics", "Beginner", "JetBrains, Google Android, JVM language, interoperability with Java, concise syntax"),
    ("Kotlin", "Syntax & Data Types", "Beginner", "val, var, String, Int, Double, Boolean, nullable types, type inference, String templates"),
    ("Kotlin", "Control Structures", "Beginner", "if expression, when expression, for, while, ranges, repeat, break, continue, labels"),
    ("Kotlin", "Functions & Lambdas", "Intermediate", "fun keyword, default parameters, named arguments, lambda expressions, higher-order functions, inline functions"),
    ("Kotlin", "Collections", "Intermediate", "List, Set, Map, mutableListOf, filter, map, groupBy, fold, sequence, collection operations"),
    ("Kotlin", "OOP - Classes & Interfaces", "Intermediate", "classes, data classes, sealed classes, object declarations, companion objects, interfaces, delegation"),
    ("Kotlin", "Advanced Features", "Advanced", "coroutines, suspend functions, Flow, extension functions, DSL builders, reified generics"),
    ("Kotlin", "Frameworks - Ktor & Android SDK", "Intermediate", "Ktor server, routing, Android Activity, Jetpack Compose, ViewModel, LiveData"),
    ("Kotlin", "File Handling & Database", "Intermediate", "File class, readText, writeText, Room database, Exposed ORM, JSON serialization"),
    ("Kotlin", "Applications - Android & Backend", "Advanced", "Android app architecture, MVVM, Kotlin Multiplatform, server-side Kotlin, microservices"),

    # Go (91-100)
    ("Go", "History & Basics", "Beginner", "Google, Rob Pike, Ken Thompson, compiled language, simplicity, concurrency focus, go run"),
    ("Go", "Syntax & Data Types", "Beginner", "var, const, int, float64, string, bool, short declaration :=, zero values, fmt package"),
    ("Go", "Control Structures", "Beginner", "if, for, switch, select, range, break, continue, defer, no while keyword"),
    ("Go", "Functions", "Intermediate", "func keyword, multiple return values, named returns, variadic functions, first-class functions, closures"),
    ("Go", "Data Structures - Slices & Maps", "Intermediate", "arrays, slices, append, make, maps, structs, pointers, nil, composite literals"),
    ("Go", "Concurrency - Goroutines & Channels", "Advanced", "goroutines, channels, select, WaitGroup, Mutex, buffered channels, deadlock prevention"),
    ("Go", "OOP-like Features", "Intermediate", "structs, methods, interfaces, embedding, composition over inheritance, type assertions"),
    ("Go", "Libraries - net/http & fmt", "Intermediate", "net/http, http.HandleFunc, JSON encoding/decoding, fmt formatting, os package, io package"),
    ("Go", "File Handling & Database", "Intermediate", "os.Open, bufio, ioutil, database/sql, GORM, JSON file I/O, error handling patterns"),
    ("Go", "Applications - Cloud & Microservices", "Advanced", "Docker, Kubernetes, gRPC, REST APIs with Gin, cloud-native development, CLI tools with Cobra"),
]

assert len(TOPIC_DEFS) == 100, f"Expected 100 topics, got {len(TOPIC_DEFS)}"


# ═══════════════════════════════════════════════════════════════════
# Gemini API caller
# ═══════════════════════════════════════════════════════════════════

async def call_gemini(prompt: str, max_tokens: int = 8000, retries: int = 3) -> str:
    """Call Gemini API with retries and backoff."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    params = {"key": GEMINI_API_KEY}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": max_tokens,
            "responseMimeType": "application/json",
        },
    }

    for attempt in range(retries):
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(url, params=params, json=payload)
                if res.status_code == 429:
                    wait = 15 * (attempt + 1)
                    log.warning(f"Rate limited, waiting {wait}s...")
                    await asyncio.sleep(wait)
                    continue
                if res.status_code in (500, 503):
                    await asyncio.sleep(5 * (attempt + 1))
                    continue
                res.raise_for_status()
                data = res.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return text.strip()
        except Exception as e:
            log.warning(f"Gemini call attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(10 * (attempt + 1))
    return ""


def extract_json(text: str):
    """Extract JSON from Gemini response, handling markdown code blocks."""
    text = text.strip()
    # Remove markdown code blocks
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object/array in the text
        for pattern in [r'\{[\s\S]*\}', r'\[[\s\S]*\]']:
            match = re.search(pattern, text)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    continue
    return None


# ═══════════════════════════════════════════════════════════════════
# YouTube API
# ═══════════════════════════════════════════════════════════════════

async def fetch_youtube_videos(topic_name: str, language: str, max_results: int = 3) -> list:
    """Fetch real YouTube videos for a topic."""
    if not YOUTUBE_API_KEY:
        return []
    query = f"{language} {topic_name} tutorial programming"
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "relevanceLanguage": "en",
        "key": YOUTUBE_API_KEY,
        "videoCategoryId": "27",  # Education
    }
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.get(url, params=params)
            if res.status_code != 200:
                return []
            data = res.json()
            videos = []
            for item in data.get("items", []):
                vid = item.get("id", {}).get("videoId", "")
                snippet = item.get("snippet", {})
                if vid:
                    videos.append({
                        "id": f"yt_{vid}",
                        "title": snippet.get("title", ""),
                        "language": language,
                        "youtubeId": vid,
                        "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
                        "duration": "",
                        "description": snippet.get("description", "")[:200],
                    })
            return videos
    except Exception as e:
        log.warning(f"YouTube fetch failed for {topic_name}: {e}")
        return []


# ═══════════════════════════════════════════════════════════════════
# Topic builder — single Gemini call per topic
# ═══════════════════════════════════════════════════════════════════

async def build_topic_with_ai(idx: int, language: str, topic_name: str, difficulty: str, brief_seed: str) -> dict:
    """Build a complete topic with AI-generated content via a single Gemini call."""
    tid = f"topic-{idx}"
    log.info(f"[{idx}/100] Generating: {language} - {topic_name}")

    # Single combined prompt for everything
    prompt = f"""Generate complete educational content for a programming topic. Return ONLY valid JSON.

Topic: "{topic_name}" in {language} programming
Difficulty: {difficulty}
Key concepts: {brief_seed}

Return a JSON object with this EXACT structure:
{{
  "overview": "A 2-3 sentence overview of this topic explaining what it covers and why it's important (150-200 words)",
  "explanations": [
    {{
      "style": "simplified",
      "title": "Simplified Explanation",
      "icon": "📝",
      "content": "A clear, jargon-free explanation in plain language. 3-4 paragraphs. Use simple words and practical examples. About 200-300 words.",
      "codeExample": "A working code example with comments (15-25 lines)"
    }},
    {{
      "style": "logical",
      "title": "Logical Breakdown",
      "icon": "🧠",
      "content": "Step 1: [first concept]\\nStep 2: [second concept]\\nStep 3: [third concept]\\nStep 4: [fourth concept]\\nStep 5: [fifth concept]\\nEach step should be a detailed sentence explaining the technical mechanics.",
      "codeExample": "A technical code example demonstrating the mechanics (15-25 lines)"
    }},
    {{
      "style": "visual",
      "title": "Visual Explanation",
      "icon": "🎨",
      "content": "Step 1: [Start] Describe the beginning of the process\\nStep 2: [Process] Describe what happens next\\nStep 3: [Check] A decision point or condition\\nStep 4: [Process] Next action\\nStep 5: [End] Final result. Format as a step-by-step flow that can be visualized.",
      "codeExample": "A code example with visual ASCII diagram in comments"
    }},
    {{
      "style": "analogy",
      "title": "Real-World Analogy",
      "icon": "💡",
      "content": "Concept A is like real-world-thing because [reason]. Concept B is like another-thing because [reason]. Continue with 3-4 analogies that make the programming concept relatable to everyday life.",
      "codeExample": "A code example that relates to the analogy"
    }}
  ],
  "quiz": [
    {{
      "question": "Actual quiz question about {topic_name}?",
      "options": ["Correct answer", "Wrong but plausible answer", "Another wrong answer", "Another wrong answer"],
      "correctAnswer": 0,
      "explanation": "Brief explanation of why the correct answer is right"
    }}
  ]
}}

IMPORTANT RULES:
1. Generate EXACTLY 10 quiz questions in the quiz array
2. Each quiz question must have exactly 4 options
3. correctAnswer is the 0-based index (0, 1, 2, or 3) - vary this across questions, don't always use 0
4. All code examples must be valid {language} code
5. Content must be educational and accurate
6. Make quiz questions progressively harder (first 3 easy, next 4 medium, last 3 hard)
7. Ensure all JSON strings are properly escaped (no unescaped quotes or newlines in strings)
8. Use \\n for newlines within string values"""

    raw = await call_gemini(prompt, max_tokens=8000)
    parsed = extract_json(raw) if raw else None

    if not parsed:
        log.warning(f"  Failed to parse AI response for topic-{idx}, using enhanced fallback")
        parsed = _build_fallback(topic_name, language, difficulty, brief_seed)

    # Validate and fix quiz
    quiz = parsed.get("quiz", [])
    validated_quiz = []
    for i, q in enumerate(quiz[:10]):
        if isinstance(q, dict) and "question" in q and "options" in q:
            opts = q["options"]
            if isinstance(opts, list) and len(opts) == 4:
                ca = q.get("correctAnswer", 0)
                if not isinstance(ca, int) or ca < 0 or ca > 3:
                    ca = 0
                validated_quiz.append({
                    "id": f"q-{idx}-{i+1}",
                    "question": str(q["question"]),
                    "options": [str(o) for o in opts],
                    "correctAnswer": ca,
                    "explanation": str(q.get("explanation", "Review the topic material for more details.")),
                    "type": "mcq",
                })
    # Pad if fewer than 10
    while len(validated_quiz) < 10:
        n = len(validated_quiz) + 1
        validated_quiz.append({
            "id": f"q-{idx}-{n}",
            "question": f"Which of the following best describes {topic_name} in {language}?",
            "options": [
                f"A core concept of {topic_name}",
                f"Unrelated to {language}",
                f"Only used in advanced scenarios",
                f"Deprecated in modern {language}",
            ],
            "correctAnswer": 0,
            "explanation": f"Understanding {topic_name} is fundamental to {language} programming.",
            "type": "mcq",
        })

    # Validate explanations
    explanations = parsed.get("explanations", [])
    validated_exps = []
    style_map = {
        "simplified": ("📝", "Simplified Explanation"),
        "logical": ("🧠", "Logical Breakdown"),
        "visual": ("🎨", "Visual Explanation"),
        "analogy": ("💡", "Real-World Analogy"),
    }
    for style_key, (icon, default_title) in style_map.items():
        found = None
        for e in explanations:
            if isinstance(e, dict) and e.get("style") == style_key:
                found = e
                break
        if found and found.get("content"):
            validated_exps.append({
                "style": style_key,
                "title": str(found.get("title", default_title)),
                "icon": icon,
                "content": str(found["content"]),
                "codeExample": str(found.get("codeExample", f"// {language} example for {topic_name}")),
            })
        else:
            validated_exps.append({
                "style": style_key,
                "title": default_title,
                "icon": icon,
                "content": f"This is the {style_key} explanation of {topic_name} in {language}. Key concepts: {brief_seed}.",
                "codeExample": f"// {language} example for {topic_name}\n// Covers: {brief_seed}",
            })

    overview = str(parsed.get("overview", f"{topic_name} is an important concept in {language} programming covering: {brief_seed}."))

    # Fetch YouTube videos
    videos = await fetch_youtube_videos(topic_name, language)

    # Build subtopic
    subtopic_id = f"sub-{idx}-1"
    subtopic = {
        "id": subtopic_id,
        "name": topic_name,
        "pdfUrl": "internal",
        "pdfTitle": f"{topic_name} - {language} Study Guide",
        "overview": overview,
        "explanations": validated_exps,
        "quiz": validated_quiz,
        "recommendedVideos": videos,
    }

    return {
        "id": tid,
        "language": language,
        "topicName": topic_name,
        "difficulty": difficulty,
        "overview": overview,
        "subtopics": [subtopic],
        "explanations": validated_exps,
        "quiz": validated_quiz,
        "recommendedVideos": videos,
    }


def _build_fallback(topic_name: str, language: str, difficulty: str, brief_seed: str) -> dict:
    """Enhanced fallback content when Gemini fails."""
    return {
        "overview": (
            f"{topic_name} is a {'fundamental' if difficulty == 'Beginner' else 'key' if difficulty == 'Intermediate' else 'advanced'} "
            f"concept in {language} programming. It covers: {brief_seed}. "
            f"Mastering this topic is essential for building real-world {language} applications and progressing as a developer."
        ),
        "explanations": [
            {
                "style": "simplified",
                "title": "Simplified Explanation",
                "icon": "📝",
                "content": f"{topic_name} in {language} is all about {brief_seed}. Think of it as one of the building blocks you need to write effective {language} code. Let's break it down into simple terms that anyone can understand.",
                "codeExample": f"// {language} - {topic_name} basic example\n// Demonstrates: {brief_seed}",
            },
            {
                "style": "logical",
                "title": "Logical Breakdown",
                "icon": "🧠",
                "content": f"Step 1: Understand the fundamentals of {topic_name}\nStep 2: Learn the syntax and key concepts: {brief_seed}\nStep 3: Practice with code examples\nStep 4: Apply to real-world problems\nStep 5: Master through repetition and projects",
                "codeExample": f"// {language} - {topic_name} technical example\n// Key: {brief_seed}",
            },
            {
                "style": "visual",
                "title": "Visual Explanation",
                "icon": "🎨",
                "content": f"Step 1: Start with {topic_name} basics\nStep 2: Process the core concepts\nStep 3: Check your understanding\nStep 4: Practice with examples\nStep 5: Master {topic_name}",
                "codeExample": f"// {language} - {topic_name} visual walkthrough\n// {brief_seed}",
            },
            {
                "style": "analogy",
                "title": "Real-World Analogy",
                "icon": "💡",
                "content": f"{topic_name} is like learning a new skill in everyday life. Just as you learn to cook by following recipes step by step, you learn {topic_name} in {language} by understanding {brief_seed} and practicing with real code.",
                "codeExample": f"// {language} - {topic_name} analogy example\n// Think of it like: {brief_seed}",
            },
        ],
        "quiz": [],  # Will be padded by the caller
    }


# ═══════════════════════════════════════════════════════════════════
# Main — generate all 100 topics
# ═══════════════════════════════════════════════════════════════════

async def main():
    client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    db = client[DB_NAME]
    log.info(f"Connected to MongoDB ({DB_NAME})")

    # Check which topics already exist (for resume)
    existing_ids = set()
    for t in db.topics.find({}, {"id": 1, "_id": 0}):
        existing_ids.add(t["id"])

    # Check if existing topics have real content (not placeholders)
    if existing_ids:
        sample = db.topics.find_one({"id": "topic-1"})
        if sample:
            q = (sample.get("quiz") or [{}])[0]
            if "Option A" in str(q.get("options", [])):
                log.info("Existing topics have placeholder content — will regenerate all")
                db.topics.drop()
                existing_ids.clear()

    total_generated = 0
    total_skipped = 0

    for idx, (lang, name, diff, seed) in enumerate(TOPIC_DEFS, start=1):
        tid = f"topic-{idx}"
        if tid in existing_ids:
            log.info(f"[{idx}/100] Skipping (exists): {lang} - {name}")
            total_skipped += 1
            continue

        topic = await build_topic_with_ai(idx, lang, name, diff, seed)
        db.topics.replace_one({"id": tid}, topic, upsert=True)
        total_generated += 1
        log.info(f"  ✅ Saved topic-{idx}: {lang} - {name} (quiz: {len(topic['quiz'])}q, videos: {len(topic['recommendedVideos'])})")

        # Rate limiting — wait between Gemini calls
        await asyncio.sleep(4)

    # Ensure indexes
    db.topics.create_index("id", unique=True)
    db.topics.create_index("language")
    db.topics.create_index("difficulty")

    # Update users with all topic IDs
    all_ids = [f"topic-{i}" for i in range(1, 101)]
    result = db.users.update_many(
        {},
        {"$set": {"pendingTopics": all_ids, "completedTopics": [], "inProgressTopics": []}}
    )

    log.info(f"\n{'='*50}")
    log.info(f"Done! Generated: {total_generated}, Skipped: {total_skipped}")
    log.info(f"Total topics in DB: {db.topics.count_documents({})}")
    log.info(f"Updated {result.modified_count} users")

    # Print language distribution
    pipeline = [{"$group": {"_id": "$language", "count": {"$sum": 1}}}, {"$sort": {"_id": 1}}]
    for doc in db.topics.aggregate(pipeline):
        log.info(f"  {doc['_id']}: {doc['count']} topics")


if __name__ == "__main__":
    asyncio.run(main())
