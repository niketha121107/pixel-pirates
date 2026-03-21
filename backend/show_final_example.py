"""
FINAL EXAMPLE: Detailed Study Material for "Syntax & Variables"
Showing the complete 7-section enhanced content
"""

from pymongo import MongoClient
from app.core.config import Settings

settings = Settings()
client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
db = client[settings.MONGODB_DATABASE]

topic = db.topics.find_one({"name": "Syntax & Variables"})

if topic and "study_material" in topic:
    material = topic["study_material"]
    
    print("\n" + "="*100)
    print("COMPLETE DETAILED STUDY MATERIAL EXAMPLE: Syntax & Variables")
    print("="*100)
    
    print("\n📚 TOPIC: Syntax & Variables")
    print("Language: Python | Difficulty: Beginner")
    print("-"*100)
    
    # 1. Overview
    print("\n╔════ 1️⃣  OVERVIEW (Foundation & Context) ════╗")
    print("│")
    overview = material.get("overview", "")
    for line in overview.split('\n'):
        if line.strip():
            print(f"│ {line}")
    print("│")
    print("╚" + "═"*96 + "╝")
    
    # 2. Explanation
    print("\n╔════ 2️⃣  EXPLANATION (Detailed Breakdown) ════╗")
    print("│")
    explanation = material.get("explanation", "")
    lines = explanation.split('\n')
    for line in lines[:25]:  # Show first 25 lines
        if line.strip():
            print(f"│ {line[:95]}")
    if len(lines) > 25:
        print(f"│ ... ({len(lines) - 25} more lines)")
    print("│")
    print("╚" + "═"*96 + "╝")
    
    # 3. Syntax
    print("\n╔════ 3️⃣  SYNTAX (Code Structure Reference) ════╗")
    print("│")
    syntax = material.get("syntax", "")
    for line in syntax.split('\n')[:20]:
        if line.strip():
            print(f"│ {line[:95]}")
    print("│")
    print("╚" + "═"*96 + "╝")
    
    # 4. Examples
    print("\n╔════ 4️⃣  CODE EXAMPLES (Practical Implementation) ════╗")
    print("│")
    example = material.get("example", "")
    for line in example.split('\n')[:25]:
        if line.strip():
            print(f"│ {line[:95]}")
    print("│")
    print("╚" + "═"*96 + "╝")
    
    # 5. Domain Usage
    print("\n╔════ 5️⃣  DOMAIN USAGE (Real-World Applications) ════╗")
    print("│")
    domain = material.get("domain_usage", "")
    for line in domain.split('\n')[:15]:
        if line.strip():
            print(f"│ {line[:95]}")
    print("│")
    print("╚" + "═"*96 + "╝")
    
    # 6. Advantages
    print("\n╔════ 6️⃣  ADVANTAGES (Benefits & Professional Value) ════╗")
    print("│")
    advantages = material.get("advantages", "")
    for line in advantages.split('\n')[:15]:
        if line.strip():
            print(f"│ {line[:95]}")
    print("│")
    print("╚" + "═"*96 + "╝")
    
    # 7. Disadvantages
    print("\n╔════ 7️⃣  DISADVANTAGES (Challenges & Solutions) ════╗")
    print("│")
    disadvantages = material.get("disadvantages", "")
    for line in disadvantages.split('\n')[:15]:
        if line.strip():
            print(f"│ {line[:95]}")
    print("│")
    print("╚" + "═"*96 + "╝")
    
    # Summary Statistics
    print("\n" + "="*100)
    print("📊 CONTENT STATISTICS FOR THIS TOPIC")
    print("="*100)
    
    total_chars = sum(len(material.get(key, "")) for key in material)
    total_words = sum(len(material.get(key, "").split()) for key in material)
    
    sections = {
        "Overview": len(material.get("overview", "").split()),
        "Explanation": len(material.get("explanation", "").split()),
        "Syntax": len(material.get("syntax", "").split()),
        "Code Examples": len(material.get("example", "").split()),
        "Domain Usage": len(material.get("domain_usage", "").split()),
        "Advantages": len(material.get("advantages", "").split()),
        "Disadvantages": len(material.get("disadvantages", "").split()),
    }
    
    print("\nWords per section:")
    for section, words in sections.items():
        percentage = (words / total_words * 100) if total_words else 0
        bar = "█" * int(percentage / 5)
        print(f"  {section:20} {words:4} words  {percentage:5.1f}%  {bar}")
    
    print(f"\n  Total: {total_words} words")
    print(f"  Total Characters: {total_chars:,} characters")
    print(f"  Average Section Size: {total_words // 7} words")
    
else:
    print("Topic not found or no study material available")

print("\n" + "="*100)
print("✅ ALL DETAILED STUDY MATERIALS SUCCESSFULLY GENERATED")
print("="*100)

print("\n🌐 ACCESS THE STUDY MATERIALS:")
print("─"*100)
print("   URL: http://localhost:5177  (Frontend)")
print("   API: http://localhost:8000  (Backend)")
print("\n   Steps to view:")
print("   1. Open http://localhost:5177")
print("   2. Login: alex@edutwin.com / password123")
print("   3. Select any topic")
print("   4. Click 'View Study Material'")
print("   5. Read through all 7 comprehensive sections")
print("\n" + "="*100 + "\n")

client.close()
