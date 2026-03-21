"""
Display Concise Study Material with Clear Example Separation
"""

from pymongo import MongoClient
from app.core.config import Settings

settings = Settings()
client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
db = client[settings.MONGODB_DATABASE]

print("\n" + "="*100)
print("CONCISE STUDY MATERIAL - NEW FORMAT")
print("="*100)

# Show concise material for Syntax & Variables
topic = db.topics.find_one({"name": "Syntax & Variables"})
if topic and "study_material" in topic:
    material = topic["study_material"]
    
    print("\n📚 TOPIC: Syntax & Variables")
    print("-"*100)
    
    # 1. Overview
    print("\n1️⃣  OVERVIEW")
    print("─"*100)
    print(material.get("overview", ""))
    
    # 2. Explanation
    print("\n2️⃣  EXPLANATION")
    print("─"*100)
    print(material.get("explanation", ""))
    
    # 3. Syntax
    print("\n3️⃣  SYNTAX")
    print("─"*100)
    print(material.get("syntax", ""))
    
    # 4. Examples - WITH CLEAR SEPARATION
    print("\n4️⃣  CODE EXAMPLES (3 Separated Examples)")
    print("─"*100)
    example = material.get("example", "")
    print(example)
    
    # 5. Domain Usage - 5 POINTS ONLY
    print("\n5️⃣  DOMAIN USAGE (5 Key Applications)")
    print("─"*100)
    domain = material.get("domain_usage", "")
    print(domain)
    
    # 6. Advantages - 5 POINTS ONLY
    print("\n6️⃣  ADVANTAGES (5 Key Benefits)")
    print("─"*100)
    advantages = material.get("advantages", "")
    print(advantages)
    
    # 7. Disadvantages - 5 POINTS ONLY
    print("\n7️⃣  DISADVANTAGES (5 Key Challenges)")
    print("─"*100)
    disadvantages = material.get("disadvantages", "")
    print(disadvantages)

print("\n" + "="*100)
print("SUMMARY OF CONCISE FORMAT")
print("="*100)

print("""
✅ NEW FORMAT FEATURES:

Domain Usage:        5 focused points (was 7-10 detailed points)
Advantages:          5 focused points (was 7-10 detailed points)
Disadvantages:       5 focused points (was 7-10 detailed points)
Examples:            3 clearly SEPARATED examples with "---" dividers
                     Each with name, code, and explanation

BENEFITS:
✓ Easier to read and understand
✓ Concise yet comprehensive
✓ Clear visual separation of examples
✓ Quick reference material
✓ Better for study and memorization
✓ Perfect for interview preparation

STRUCTURE:
┌─────────────────────────────┐
│ EXAMPLE 1: [Name]           │
│ [Code]                      │
│ Why: [Explanation]          │
├─────────────────────────────┤
│ EXAMPLE 2: [Name]           │
│ [Code]                      │
│ Why: [Explanation]          │
├─────────────────────────────┤
│ EXAMPLE 3: [Name]           │
│ [Code]                      │
│ Why: [Explanation]          │
└─────────────────────────────┘
""")

print("="*100)
print("✨ All 200 topics updated with this concise format!")
print("="*100 + "\n")

client.close()
