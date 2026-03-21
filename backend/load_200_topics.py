#!/usr/bin/env python
"""Load your exact 200 topics into MongoDB"""
from pymongo import MongoClient
from app.core.config import Settings
from datetime import datetime

settings = Settings()
client = MongoClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DATABASE]

# Drop entire collection to clear indexes
db.topics.drop()
print("✓ Dropped topics collection\n")

topics_col = db.topics

# Your exact 200 topics
TOPICS = {
    "Python": ["Syntax & Variables", "Data Types", "Control Structures", "Functions", "OOP Concepts", "Modules & Packages", "File Handling", "Exception Handling", "Libraries (NumPy, Pandas)", "Web/AI Frameworks"],
    "JavaScript": ["Basics & Syntax", "DOM Manipulation", "Functions & Scope", "Events Handling", "ES6+ Features", "Async Programming (Promises, Async/Await)", "APIs & Fetch", "Frameworks (React, Angular)", "Node.js Basics", "Error Handling"],
    "Java": ["Basics & Syntax", "Data Types", "OOP Concepts", "Collections Framework", "Exception Handling", "File I/O", "Multithreading", "JDBC", "Servlets & JSP", "Spring Framework"],
    "C++": ["Basics & Syntax", "Pointers", "OOP Concepts", "STL", "Memory Management", "File Handling", "Templates", "Exception Handling", "Multithreading", "Competitive Programming"],
    "C": ["Basics & Syntax", "Data Types", "Control Structures", "Functions", "Arrays & Strings", "Pointers", "Structures & Unions", "File Handling", "Memory Allocation", "Preprocessor Directives"],
    "C#": ["Basics & Syntax", "OOP Concepts", ".NET Framework", "Collections", "LINQ", "Exception Handling", "File Handling", "Async Programming", "Windows Apps", "Unity Game Dev"],
    "Go": ["Basics & Syntax", "Data Types", "Functions", "Structs & Interfaces", "Goroutines", "Channels", "Concurrency", "Error Handling", "Web Development", "Packages"],
    "Rust": ["Basics & Syntax", "Ownership Model", "Borrowing & Lifetimes", "Data Types", "Pattern Matching", "Error Handling", "Concurrency", "Modules", "Cargo Package Manager", "Systems Programming"],
    "Kotlin": ["Basics & Syntax", "Null Safety", "Functions", "OOP Concepts", "Collections", "Coroutines", "Android Development", "Extensions", "Lambdas", "Interoperability with Java"],
    "Swift": ["Basics & Syntax", "Optionals", "Functions", "OOP Concepts", "Closures", "Protocols", "Memory Management", "Error Handling", "iOS Development", "SwiftUI"],
    "TypeScript": ["Types System", "Interfaces", "Classes", "Functions", "Generics", "Modules", "Decorators", "Async Programming", "Integration with JS", "Framework Usage"],
    "PHP": ["Basics & Syntax", "Forms Handling", "Sessions & Cookies", "File Handling", "MySQL Integration", "OOP Concepts", "Security", "APIs", "Frameworks (Laravel)", "Error Handling"],
    "Ruby": ["Basics & Syntax", "Data Types", "OOP Concepts", "Blocks & Iterators", "Modules", "Exception Handling", "File Handling", "Gems", "Rails Framework", "Testing"],
    "Dart": ["Basics & Syntax", "Data Types", "Functions", "OOP Concepts", "Async Programming", "Streams", "Collections", "Null Safety", "Flutter Basics", "Packages"],
    "R": ["Basics & Syntax", "Data Structures", "Data Manipulation", "Visualization", "Statistics", "Packages", "Data Cleaning", "Machine Learning", "Reporting", "Time Series"],
    "MATLAB": ["Basics & Syntax", "Matrices & Arrays", "Plotting", "Functions", "Scripts", "Toolboxes", "Simulations", "Data Analysis", "Image Processing", "Control Systems"],
    "SQL": ["Basics & Syntax", "CRUD Operations", "Joins", "Constraints", "Indexes", "Subqueries", "Views", "Stored Procedures", "Transactions", "Optimization"],
    "Assembly language": ["Architecture Basics", "Registers", "Instructions", "Addressing Modes", "Memory Management", "Stack Operations", "Interrupts", "Macros", "Debugging", "Embedded Systems"],
    "Scala": ["Basics & Syntax", "Functional Programming", "OOP Concepts", "Collections", "Pattern Matching", "Concurrency", "Futures", "Akka Framework", "Spark Integration", "JVM Interoperability"],
    "Shell": ["Basics & Commands", "Variables", "Control Structures", "Functions", "File Operations", "Process Management", "Pipes & Redirection", "Scheduling (Cron)", "Text Processing (awk, sed)", "Automation Scripts"],
}

print("\n" + "="*70)
print("LOADING YOUR 200 EXACT TOPICS")
print("="*70 + "\n")

all_topics = []
for language, topics in TOPICS.items():
    for idx, topic_name in enumerate(topics, 1):
        all_topics.append({
            "name": topic_name,
            "language": language,
            "difficulty": "Beginner" if idx <= 3 else ("Intermediate" if idx <= 7 else "Advanced"),
            "overview": f"{topic_name} in {language}",
            "created_at": datetime.now()
        })

result = topics_col.insert_many(all_topics)
print(f"✓ Inserted {len(result.inserted_ids)} topics\n")

# Verify
by_language = {}
for language in TOPICS.keys():
    count = topics_col.count_documents({"language": language})
    by_language[language] = count
    print(f"  {language}: {count} topics")

total = sum(by_language.values())
print(f"\n{'='*70}")
print(f"✅ TOTAL: {total}/200 topics loaded")
print(f"{'='*70}\n")

client.close()
