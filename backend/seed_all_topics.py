"""
Seed database with full 102 programming topics.
Run: python seed_all_topics.py
"""

import pymongo
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

def connect_mongodb():
    """Connect to MongoDB."""
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)
        client.admin.command("ping")
        db = client["pixel_pirates"]
        return db
    except Exception as e:
        log.error(f"❌ MongoDB connection failed: {e}")
        return None

def seed_topics():
    """Seed 102 comprehensive programming topics."""
    db = connect_mongodb()
    if db is None:
        return

    # Clear existing topics
    db.topics.delete_many({})
    log.info("🗑️  Cleared existing topics")

    # Define 102 topics across 10 programming languages
    topics = []
    topic_id = 1
    
    # Python (1-12)
    python_topics = [
        "History & Philosophy", "Syntax & Basics", "Control Structures", 
        "Functions & Recursion", "Data Structures", "OOP - Classes & Inheritance",
        "Advanced Features", "Libraries - NumPy, Pandas, Flask",
        "File Handling & Databases", "Applications - AI/ML & Web Dev",
        "Decorators & Generators", "Async Programming"
    ]
    
    # JavaScript (13-24)
    javascript_topics = [
        "History & ECMAScript", "Syntax & Basics (ES6+)", "Control Structures",
        "Functions & Closures", "Data Structures", "OOP - Prototypes & Classes",
        "Advanced Features", "Libraries - React & Node.js", "Web APIs & DOM",
        "Async & Promises", "TypeScript Basics", "Modern Frameworks"
    ]
    
    # Java (25-36)
    java_topics = [
        "History & JVM", "Syntax & Basics", "Control Structures",
        "Functions & Methods", "Arrays & Collections", "OOP - Classes & Inheritance",
        "Advanced Features", "Spring Framework", "Database & JDBC",
        "Concurrency & Threading", "Design Patterns", "Performance & Optimization"
    ]
    
    # C++ (37-48)
    cpp_topics = [
        "History & Compilation", "Syntax & Basics", "Control Structures",
        "Functions & Pointers", "Memory Management", "OOP - Classes & Inheritance",
        "STL & Containers", "Advanced Features", "File I/O", 
        "Concurrency", "Performance Optimization", "Game Development Basics"
    ]
    
    # C# (49-60)
    csharp_topics = [
        "History & .NET", "Syntax & Basics", "Control Structures",
        "Methods & Delegates", "Collections", "OOP - Classes & Inheritance",
        "LINQ & Async", "ASP.NET & Web Dev", "Entity Framework",
        "WPF & UI", "Dependency Injection", "Cloud Integration"
    ]
    
    # Go (61-72)
    go_topics = [
        "History & Philosophy", "Syntax & Basics", "Control Structures",
        "Functions & Packages", "Data Structures", "OOP - Interfaces",
        "Goroutines & Channels", "Web Development", "Concurrency Patterns",
        "Testing & Benchmarking", "Command Line Tools", "Microservices"
    ]
    
    # Rust (73-84)
    rust_topics = [
        "History & Philosophy", "Syntax & Basics", "Ownership System",
        "Functions & Control Flow", "Structs & Enums", "Traits & Generics",
        "Error Handling", "Concurrency & Async", "Web Development",
        "Memory Safety", "Performance Optimization", "Systems Programming"
    ]
    
    # SQL (85-92)
    sql_topics = [
        "Database Basics", "SELECT & WHERE", "JOINs & Relationships",
        "Aggregations & GROUP BY", "Subqueries", "Indexes & Performance",
        "Transactions & ACID", "Advanced SQL"
    ]
    
    # TypeScript (93-98)
    typescript_topics = [
        "Intro & Setup", "Types & Interfaces", "Advanced Types",
        "Decorators", "Namespaces & Modules", "Integration with React"
    ]
    
    # Kotlin (99-102)
    kotlin_topics = [
        "Intro from Java", "Syntax & Null Safety", "Functional Programming", "Coroutines"
    ]

    all_language_topics = [
        ("Python", python_topics),
        ("JavaScript", javascript_topics),
        ("Java", java_topics),
        ("C++", cpp_topics),
        ("C#", csharp_topics),
        ("Go", go_topics),
        ("Rust", rust_topics),
        ("SQL", sql_topics),
        ("TypeScript", typescript_topics),
        ("Kotlin", kotlin_topics),
    ]

    for language, topic_names in all_language_topics:
        for topic_name in topic_names:
            topic = {
                "id": f"topic-{topic_id}",
                "topicName": f"{topic_name}",
                "language": language,
                "difficulty": "Intermediate",
                "overview": f"Learn about {topic_name} in {language}. This comprehensive topic covers all aspects of {topic_name.lower()} with practical examples and best practices.",
                "explanations": [
                    {
                        "style": "simplified",
                        "title": "Simplified",
                        "content": f"Easy explanation of {topic_name} for beginners.",
                        "icon": "📝"
                    },
                    {
                        "style": "logical",
                        "title": "Logical",
                        "content": f"Step-by-step logical explanation of {topic_name}.",
                        "icon": "🧠"
                    },
                    {
                        "style": "visual",
                        "title": "Visual",
                        "content": f"Visual diagrams and flowcharts for {topic_name}.",
                        "icon": "🎨"
                    },
                    {
                        "style": "analogy",
                        "title": "Analogy",
                        "content": f"Real-world analogy for understanding {topic_name}.",
                        "icon": "🔗"
                    }
                ],
                "quiz": [
                    {
                        "id": f"q1-{topic_id}",
                        "question": f"What is {topic_name}?",
                        "options": [
                            f"Option A about {topic_name}",
                            "Option B",
                            "Option C",
                            "Option D"
                        ],
                        "correct": 0,
                        "explanation": f"This is the correct answer for {topic_name}."
                    }
                ],
                "recommendedVideos": [
                    {
                        "title": f"{topic_name} Tutorial",
                        "youtubeId": "dQw4w9WgXcQ",
                        "channel": "Programming Channel",
                        "duration": "15:30",
                        "views": 100000
                    }
                ],
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
                "status": "active"
            }
            topics.append(topic)
            topic_id += 1

    # Insert all topics
    if topics:
        result = db.topics.insert_many(topics)
        log.info(f"✅ Inserted {len(result.inserted_ids)} topics")
    
    # Verify
    count = db.topics.count_documents({})
    log.info(f"\n📊 Verification:")
    log.info(f"   topics: {count} documents")
    
    if count == 102:
        log.info(f"\n🎉 Successfully seeded {count} topics!")
    else:
        log.warning(f"⚠️  Expected 102 topics but found {count}")

if __name__ == "__main__":
    seed_topics()
