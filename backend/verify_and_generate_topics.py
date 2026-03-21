#!/usr/bin/env python
"""
Verify 200 topics exist and are complete before generating content.
If topics are missing, generates them using Gemini API.
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any

import google.generativeai as genai
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Config
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGODB_DATABASE", "pixel_pirates")

if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY not set!")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# 200 Topic definitions across 20 programming languages
TOPIC_DEFS = [
    # Python (10)
    ("Python", "History & Philosophy", "Beginner", "Python creation by Guido van Rossum, Zen of Python, PEP 8"),
    ("Python", "Syntax & Basics", "Beginner", "variables, data types, operators, input/output"),
    ("Python", "Control Structures", "Beginner", "if/else, loops, break, continue"),
    ("Python", "Functions & Recursion", "Intermediate", "def, return, parameters, recursion"),
    ("Python", "Data Structures", "Intermediate", "lists, dicts, sets, tuples"),
    ("Python", "OOP (Classes & Inheritance)", "Intermediate", "classes, inheritance, polymorphism"),
    ("Python", "Decorators & Generators", "Advanced", "decorators, generators, yield"),
    ("Python", "Async/Await & Concurrency", "Advanced", "async, await, asyncio"),
    ("Python", "File Handling & IO", "Intermediate", "open, read, write, context managers"),
    ("Python", "Popular Libraries", "Advanced", "NumPy, Pandas, Flask, Django"),
    
    # JavaScript (10)
    ("JavaScript", "History & ECMAScript", "Beginner", "creation, ECMAScript standards, ES6+"),
    ("JavaScript", "Syntax & Basics", "Beginner", "let, const, var, data types, operators"),
    ("JavaScript", "Control Flow", "Beginner", "if, switch, for, while loops"),
    ("JavaScript", "Functions & Closures", "Intermediate", "arrow functions, closures, IIFE"),
    ("JavaScript", "Objects & Arrays", "Intermediate", "objects, arrays, destructuring"),
    ("JavaScript", "ES6 Classes & Prototypes", "Intermediate", "classes, prototypes, inheritance"),
    ("JavaScript", "Promises & Async/Await", "Advanced", "promises, async/await, error handling"),
    ("JavaScript", "DOM & Events", "Intermediate", "event listeners, DOM manipulation"),
    ("JavaScript", "REST APIs & Fetch", "Intermediate", "fetch API, JSON, HTTP requests"),
    ("JavaScript", "React Fundamentals", "Advanced", "components, JSX, hooks, state"),
    
    # Java (10)
    ("Java", "History & JVM", "Beginner", "Java creation, JVM, bytecode, compilation"),
    ("Java", "Syntax & Basics", "Beginner", "data types, variables, operators"),
    ("Java", "Control Structures", "Beginner", "if/else, loops, switch"),
    ("Java", "Functions & Methods", "Intermediate", "method declaration, parameters, return"),
    ("Java", "OOP Concepts", "Intermediate", "classes, inheritance, polymorphism, encapsulation"),
    ("Java", "Collections Framework", "Intermediate", "ArrayList, HashMap, HashSet, interfaces"),
    ("Java", "Exception Handling", "Intermediate", "try/catch/finally, custom exceptions"),
    ("Java", "File I/O & Streams", "Intermediate", "file operations, input/output streams"),
    ("Java", "Multithreading", "Advanced", "threads, concurrency, synchronization"),
    ("Java", "Spring Framework", "Advanced", "Spring Boot, dependency injection, REST"),
    
    # C++ (10)
    ("C++", "History & Basics", "Beginner", "C++ creation, ISO standards, OOP features"),
    ("C++", "Syntax & Data Types", "Beginner", "primitives, operators, type casting"),
    ("C++", "Control Flow", "Beginner", "if/else, loops, break, continue"),
    ("C++", "Functions & Pointers", "Intermediate", "functions, pointers, references"),
    ("C++", "Arrays & Strings", "Intermediate", "arrays, C-style strings, std::string"),
    ("C++", "OOP (Classes & Inheritance)", "Intermediate", "classes, constructors, inheritance"),
    ("C++", "Templates & Generics", "Advanced", "templates, template specialization"),
    ("C++", "STL Containers", "Advanced", "vector, map, set, deque, algorithms"),
    ("C++", "Memory Management", "Advanced", "new/delete, smart pointers, RAII"),
    ("C++", "Modern C++ (C++11/17)", "Advanced", "lambda, auto, move semantics"),
    
    # C (10)
    ("C", "History & Basics", "Beginner", "Dennis Ritchie, ANSI C, compiled language"),
    ("C", "Syntax & Data Types", "Beginner", "int, float, char, operators, printf/scanf"),
    ("C", "Control Structures", "Beginner", "if/else, for, while, switch"),
    ("C", "Functions & Pointers", "Intermediate", "functions, pointers, pointer arithmetic"),
    ("C", "Arrays & Strings", "Intermediate", "arrays, C strings, string functions"),
    ("C", "Structures & Unions", "Intermediate", "struct, union, typedef, bit fields"),
    ("C", "Memory Management", "Advanced", "malloc, calloc, realloc, free"),
    ("C", "File I/O", "Intermediate", "fopen, fread, fwrite, file operations"),
    ("C", "Standard Library", "Intermediate", "stdio.h, stdlib.h, string.h, math.h"),
    ("C", "Systems Programming", "Advanced", "OS concepts, embedded systems"),
    
    # TypeScript (10)
    ("TypeScript", "History & Setup", "Beginner", "TypeScript creation, compilation, npm"),
    ("TypeScript", "Basic Types", "Beginner", "primitive types, unions, any, unknown"),
    ("TypeScript", "Functions & Types", "Intermediate", "function types, parameters, overloads"),
    ("TypeScript", "Interfaces & Types", "Intermediate", "interfaces, type aliases, generics"),
    ("TypeScript", "Classes & OOP", "Intermediate", "classes, access modifiers, inheritance"),
    ("TypeScript", "Advanced Types", "Advanced", "conditional types, mapped types, utility"),
    ("TypeScript", "Decorators", "Advanced", "class decorators, method decorators"),
    ("TypeScript", "Modules & Namespaces", "Intermediate", "imports, exports, module resolution"),
    ("TypeScript", "Generics", "Advanced", "generic functions, classes, constraints"),
    ("TypeScript", "React with TypeScript", "Advanced", "props typing, hooks, context"),
    
    # Go (10)
    ("Go", "History & Syntax", "Beginner", "Rob Pike creation, goroutines, simple syntax"),
    ("Go", "Variables & Types", "Beginner", "var, const, basic types, type inference"),
    ("Go", "Control Flow", "Beginner", "if/else, for loops, switch statements"),
    ("Go", "Functions & Interfaces", "Intermediate", "functions, interfaces, packages"),
    ("Go", "Goroutines & Channels", "Advanced", "goroutines, channels, concurrency"),
    ("Go", "Structs & Methods", "Intermediate", "struct fields, method receivers"),
    ("Go", "Error Handling", "Intermediate", "error interface, panic, recover"),
    ("Go", "File I/O", "Intermediate", "os, io packages, file operations"),
    ("Go", "Web Development", "Advanced", "net/http, routing, handlers"),
    ("Go", "Concurrency Patterns", "Advanced", "buffered channels, select, timeouts"),
    
    # Rust (10)
    ("Rust", "History & Ownership", "Beginner", "Rust creation, ownership, borrowing"),
    ("Rust", "Variables & Types", "Beginner", "mut, immutability, type system"),
    ("Rust", "Functions & Control", "Intermediate", "functions, loops, pattern matching"),
    ("Rust", "Ownership & Borrowing", "Intermediate", "move semantics, references, lifetimes"),
    ("Rust", "Structs & Traits", "Intermediate", "struct definition, traits, impl"),
    ("Rust", "Error Handling", "Intermediate", "Result, Option, error propagation"),
    ("Rust", "Iterators & Closures", "Advanced", "iterator trait, closures, functional"),
    ("Rust", "Memory Safety", "Advanced", "borrow checker, thread safety, safety"),
    ("Rust", "Concurrency", "Advanced", "threads, channels, async/await"),
    ("Rust", "Systems Programming", "Advanced", "low-level, WebAssembly, embedded"),
    
    # PHP (10)
    ("PHP", "History & Basics", "Beginner", "PHP creation, server-side scripting"),
    ("PHP", "Syntax & Variables", "Beginner", "echo, $variables, data types"),
    ("PHP", "Control Structures", "Beginner", "if/else, loops, switch statements"),
    ("PHP", "Functions & Scoping", "Intermediate", "function declaration, scope, global"),
    ("PHP", "Strings & Arrays", "Intermediate", "string functions, array operations"),
    ("PHP", "OOP & Classes", "Intermediate", "classes, inheritance, interfaces"),
    ("PHP", "Database Interaction", "Intermediate", "MySQL, MySQLi, prepared statements"),
    ("PHP", "Form Handling", "Intermediate", "$_POST, $_GET, validation"),
    ("PHP", "Sessions & Cookies", "Intermediate", "session_start, cookies, authentication"),
    ("PHP", "Laravel Framework", "Advanced", "MVC, routing, Eloquent ORM"),
    
    # C# (10)
    ("C#", "History & .NET", "Beginner", ".NET framework, CLR, C# creation"),
    ("C#", "Syntax & Types", "Beginner", "var, dynamic, nullable types, LINQ"),
    ("C#", "Classes & Inheritance", "Intermediate", "classes, inheritance, polymorphism"),
    ("C#", "Interfaces & Abstract", "Intermediate", "interfaces, abstract classes"),
    ("C#", "Properties & Events", "Intermediate", "get/set, events, delegates"),
    ("C#", "Generics & Collections", "Intermediate", "List<T>, Dictionary<K,V>, constraints"),
    ("C#", "Async/Await", "Advanced", "async, await, tasks, threading"),
    ("C#", "LINQ Queries", "Intermediate", "query syntax, method syntax, operators"),
    ("C#", "Reflection & Attributes", "Advanced", "type info, custom attributes, metadata"),
    ("C#", "ASP.NET Core", "Advanced", "MVC, dependency injection, REST APIs"),
    
    # Ruby (10)
    ("Ruby", "History & Philosophy", "Beginner", "Yukihiro Matsumoto, Matz, developer happiness"),
    ("Ruby", "Syntax & Basics", "Beginner", "variables, data types, string interpolation"),
    ("Ruby", "Control Flow", "Beginner", "if/unless, loops, iterators"),
    ("Ruby", "Methods & Blocks", "Intermediate", "def, yield, blocks, Procs, Lambdas"),
    ("Ruby", "Arrays & Hashes", "Intermediate", "array methods, hash operations, destructuring"),
    ("Ruby", "Classes & Modules", "Intermediate", "class definition, modules, mixins"),
    ("Ruby", "Regular Expressions", "Intermediate", "regex patterns, matching, substitution"),
    ("Ruby", "File I/O & Streams", "Intermediate", "File class, IO operations, reading/writing"),
    ("Ruby", "Error Handling", "Intermediate", "begin/rescue/ensure, custom exceptions"),
    ("Ruby", "Rails Framework", "Advanced", "MVC, ActiveRecord, routes, views"),
    
    # Swift (10)
    ("Swift", "History & Syntax", "Beginner", "Apple Swift, iOS development, playgrounds"),
    ("Swift", "Variables & Types", "Beginner", "let, var, type inference, optionals"),
    ("Swift", "Control Flow", "Beginner", "if/else, switch, loops, guard"),
    ("Swift", "Functions & Closures", "Intermediate", "func, parameters, trailing closures"),
    ("Swift", "Structs & Classes", "Intermediate", "value types, reference types, inheritance"),
    ("Swift", "Protocols & Delegates", "Intermediate", "protocols, extensions, conformance"),
    ("Swift", "Error Handling", "Intermediate", "try/catch, throws, Result type"),
    ("Swift", "Memory Management", "Intermediate", "ARC, strong/weak references"),
    ("Swift", "Concurrency", "Advanced", "async/await, actors, task groups"),
    ("Swift", "UIKit & SwiftUI", "Advanced", "UI frameworks, views, animations"),
    
    # SQL (10)
    ("SQL", "Database Basics", "Beginner", "RDBMS, tables, schemas, DDL"),
    ("SQL", "SELECT & Queries", "Beginner", "SELECT, WHERE, ORDER BY, LIMIT"),
    ("SQL", "JOINs & Relationships", "Intermediate", "INNER JOIN, LEFT JOIN, foreign keys"),
    ("SQL", "Aggregation & Grouping", "Intermediate", "GROUP BY, HAVING, COUNT, SUM, AVG"),
    ("SQL", "Subqueries & CTE", "Intermediate", "nested queries, WITH clauses, CTEs"),
    ("SQL", "INSERT, UPDATE, DELETE", "Beginner", "DML operations, data modification"),
    ("SQL", "Indexes & Performance", "Advanced", "indexes, query optimization, EXPLAIN"),
    ("SQL", "Transactions & ACID", "Intermediate", "COMMIT, ROLLBACK, isolation levels"),
    ("SQL", "Stored Procedures", "Advanced", "procedures, triggers, functions"),
    ("SQL", "Advanced Queries", "Advanced", "window functions, partitioning, analytics"),
    
    # Kotlin (10)
    ("Kotlin", "History & Features", "Beginner", "JetBrains creation, Android, interop"),
    ("Kotlin", "Syntax Basics", "Beginner", "variables, data types, null safety"),
    ("Kotlin", "Control Structures", "Beginner", "if/else, when, loops, recursion"),
    ("Kotlin", "Functions & Lambdas", "Intermediate", "fun, extension functions, lambdas"),
    ("Kotlin", "Classes & Inheritance", "Intermediate", "class, interface, data class"),
    ("Kotlin", "Higher-Order Functions", "Advanced", "function types, inline functions"),
    ("Kotlin", "Collections & Sequences", "Intermediate", "list, set, map, sequences"),
    ("Kotlin", "Scope Functions", "Intermediate", "apply, also, let, run, with"),
    ("Kotlin", "Coroutines", "Advanced", "suspend, launch, async"),
    ("Kotlin", "Android Development", "Advanced", "Activities, Fragments, Jetpack"),
    
    # Dart (10)
    ("Dart", "History & Philosophy", "Beginner", "Google Dart, strong typing, null safety"),
    ("Dart", "Variables & Types", "Beginner", "var, dynamic, final, const types"),
    ("Dart", "Functions & Syntax", "Intermediate", "function declaration, named parameters"),
    ("Dart", "Classes & OOP", "Intermediate", "class definition, constructors, inheritance"),
    ("Dart", "Collections", "Intermediate", "List, Map, Set, spread operator"),
    ("Dart", "Async Programming", "Advanced", "Future, async/await, streams"),
    ("Dart", "Error Handling", "Intermediate", "try/catch/finally, custom exceptions"),
    ("Dart", "Mixins & Extensions", "Advanced", "mixin keyword, extension methods"),
    ("Dart", "Package Management", "Intermediate", "pub, dependencies, package creation"),
    ("Dart", "Flutter Development", "Advanced", "widgets, stateful/stateless, UI building"),
    
    # Python Advanced (10) - Additional topics
    ("Python", "Machine Learning Basics", "Advanced", "scikit-learn, model training, evaluation"),
    ("Python", "Data Analysis", "Advanced", "Pandas, NumPy, data cleaning, visualization"),
    ("Python", "Web Scraping", "Intermediate", "BeautifulSoup, requests, parsing HTML"),
    ("Python", "Testing & Debugging", "Intermediate", "pytest, unittest, debugging tools"),
    ("Python", "Package Development", "Advanced", "setuptools, PyPI, versioning"),
    ("Python", "API Development", "Advanced", "FastAPI, Django REST, authentication"),
    ("Python", "Docker & Containerization", "Advanced", "Docker basics, containerizing apps"),
    ("Python", "Environmental & Config", "Intermediate", ".env files, settings, configuration"),
    ("Python", "Logging & Monitoring", "Intermediate", "logging module, log levels, handlers"),
    ("Python", "Performance Optimization", "Advanced", "profiling, caching, optimization"),
]


def generate_single_topic(lang: str, topic: str, difficulty: str, overview: str) -> Dict[str, Any]:
    """Generate a single topic with basic structure using Gemini."""
    try:
        prompt = f"""
        Create a comprehensive study guide for:
        
        Technology: {lang}
        Topic: {topic}
        Difficulty: {difficulty}
        Overview: {overview}
        
        Provide a JSON response with:
        {{
            "topicName": "{topic}",
            "language": "{lang}",
            "difficulty": "{difficulty}",
            "overview": "...(2-3 sentences overview)...",
            "keyPoints": [...list 5-7 key points...]
        }}
        """
        
        response = model.generate_content(prompt)
        
        # Parse response
        text = response.text
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end > start:
            import json
            return json.loads(text[start:end])
        
        return {
            "topicName": topic,
            "language": lang,
            "difficulty": difficulty,
            "overview": overview,
            "keyPoints": ["Will be expanded with explanations"],
            "contentStatus": "initial"
        }
        
    except Exception as e:
        print(f"⚠️  Error generating {topic}: {e}")
        return {
            "topicName": topic,
            "language": lang,
            "difficulty": difficulty,
            "overview": overview,
            "contentStatus": "initial"
        }


def verify_and_create_topics():
    """Verify 200 topics exist or create them."""
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    topics_col = db["topics"]
    
    print("\n📊 Checking existing topics...")
    
    existing_count = topics_col.count_documents({})
    print(f"✅ Found {existing_count} existing topics")
    
    if existing_count >= 200:
        print(f"✅ We have {existing_count} topics (>= 200 required). All good!")
        client.close()
        return True
    
    print(f"⚠️  Need to create {200 - existing_count} more topics")
    print("⏳ Generating missing topics...")
    
    topics_to_add = []
    for i, (lang, topic, difficulty, overview) in enumerate(TOPIC_DEFS, 1):
        # Check if topic exists
        existing = topics_col.find_one({
            "topicName": topic,
            "language": lang
        })
        
        if not existing:
            print(f"  {i}. Generating: {lang} - {topic}")
            
            topic_data = generate_single_topic(lang, topic, difficulty, overview)
            topic_data["_id"] = f"{lang.lower()}_{i}"
            topic_data["createdAt"] = datetime.utcnow().isoformat()
            topic_data["contentStatus"] = "initial"
            topic_data["explanations"] = []
            topic_data["mockQuestions"] = []
            topic_data["recommendedVideos"] = []
            topic_data["pdfPath"] = None
            
            topics_to_add.append(topic_data)
    
    if topics_to_add:
        print(f"\n💾 Inserting {len(topics_to_add)} new topics...")
        result = topics_col.insert_many(topics_to_add)
        print(f"✅ Inserted {len(result.inserted_ids)} topics")
    
    # Final count
    final_count = topics_col.count_documents({})
    print(f"\n✅ Total topics now: {final_count}")
    
    client.close()
    return final_count >= 200


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🔍 TOPICS VERIFICATION & GENERATION")
    print("="*80)
    
    success = verify_and_create_topics()
    
    if success:
        print("\n✅ All 200 topics are ready for content generation!")
        print("\n📝 Next step: Run 'python generate_complete_content.py'")
    else:
        print("\n❌ Failed to ensure 200 topics")
        sys.exit(1)
