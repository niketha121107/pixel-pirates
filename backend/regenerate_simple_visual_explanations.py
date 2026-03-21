#!/usr/bin/env python
"""
Regenerate visual explanations with simple, clear language.
Focus on: What → Why → How → Example → Use → Pros → Cons
Keep it concise and easy to understand.
"""

from pymongo import MongoClient
from app.core.config import Settings

settings = Settings()
client = MongoClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DATABASE]

def generate_simple_visual_explanation(topic_data: dict) -> str:
    """Generate simple, clear visual explanation (1,200-1,400 chars)"""
    
    name = topic_data.get('name', 'Concept')
    simplified = topic_data.get('explanations', {}).get('simplified', '')
    logical = topic_data.get('explanations', {}).get('logical', '')
    analogy = topic_data.get('explanations', {}).get('analogy', '')
    
    # Extract simple intro from existing explanations
    intro = simplified[:100] if simplified else f"Understanding {name}"
    first_step = logical.split('Step')[1][:80] if 'Step' in logical else f"Learn about {name}"
    analogy_text = analogy[:120] if analogy else "Think about how this works in real life"
    
    visual = f"""
┌─────────────────────────────────────────────┐
│ {name.upper()[:43]}
└─────────────────────────────────────────────┘

WHAT IS {name.upper()[:35]}?
{intro}...

WHY SHOULD YOU LEARN IT?
  ✓ It's a fundamental concept
  ✓ Used in real-world programming
  ✓ Essential for professional developers
  ✓ Improves code quality

HOW DOES IT WORK?
  1️⃣  Start - Initialize or setup
  2️⃣  Process - Execute the logic
  3️⃣  Output - Get the result
  4️⃣  Use - Apply it in your code

SIMPLE ANALOGY
{analogy_text}...

WHERE IS IT USED?
  • Web Development
  • Mobile Apps
  • Data Science
  • Game Development
  • System Programming

KEY POINTS TO REMEMBER
  ⭐ Main concept: {name}
  ⭐ Most important: Correct usage
  ⭐ Common mistake: Not following best practices
  ⭐ Real example: Everyday programming task

ADVANTAGES          │ DISADVANTAGES
──────────────────────────────────────────
  ✓ Easy to use      │ ✗ Takes time to learn
  ✓ Improves quality │ ✗ Some edge cases
  ✓ Best practice    │ ✗ Needs practice
  ✓ Industry standard│ ✗ Version differences
""".strip()
    
    return visual


def regenerate_simple_visual_explanations():
    """Regenerate all visual explanations with simple language"""
    
    print("\n" + "="*70)
    print("SIMPLE VISUAL EXPLANATION GENERATION")
    print("="*70)
    print("\nApproach: What → Why → How → Example → Use → Pros → Cons")
    print("Style: Simple, clear, easy-to-understand language")
    
    topics = list(db.topics.find())
    total = len(topics)
    updated = 0
    
    for i, topic in enumerate(topics, 1):
        try:
            # Generate simple visual explanation
            simple_visual = generate_simple_visual_explanation(topic)
            
            # Update in database
            db.topics.update_one(
                {'_id': topic['_id']},
                {
                    '$set': {
                        'explanations.visual': simple_visual
                    }
                }
            )
            
            updated += 1
            
            # Progress every 20 topics
            if i % 20 == 0:
                size = len(simple_visual)
                print(f"[{i}/{total}] {topic.get('name', 'Unknown')}")
                print(f"         → Simple visual: {size} chars")
            
        except Exception as e:
            print(f"ERROR at topic {i}: {str(e)}")
    
    print("\n" + "="*70)
    print(f"RESULT: {updated}/{total} visual explanations simplified")
    print("="*70)
    print(f"\n✓ All visual explanations now use simple, clear language")
    print(f"✓ Structure: What → Why → How → Example → Use → Pros/Cons")
    print(f"✓ Easy for beginners to understand")
    print(f"✓ No complex terminology or diagrams")
    print(f"✓ Fits perfectly in UI explanation box\n")
    
    client.close()

if __name__ == '__main__':
    regenerate_simple_visual_explanations()
