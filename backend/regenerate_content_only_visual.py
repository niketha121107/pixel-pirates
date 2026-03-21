#!/usr/bin/env python
"""
Regenerate visual explanations with ONLY content text - no formatting lines or decorations
"""

from pymongo import MongoClient
from app.core.config import Settings

settings = Settings()
client = MongoClient(settings.MONGODB_URL)
db = client[settings.MONGODB_DATABASE]

def generate_content_only_visual(topic_data: dict) -> str:
    """Generate visual explanation with ONLY content - no decorative lines or boxes"""
    
    name = topic_data.get('name', 'Concept')
    simplified = topic_data.get('explanations', {}).get('simplified', '')
    logical = topic_data.get('explanations', {}).get('logical', '')
    analogy = topic_data.get('explanations', {}).get('analogy', '')
    
    # Extract intro
    intro = simplified[:100] if simplified else f"Understanding {name}"
    
    visual = f"""WHAT IS {name.upper()[:30]}?
{intro}...

WHY LEARN IT?
It's a fundamental concept used in real-world programming.
Essential for professional developers.
Improves overall code quality.
Industry standard practice.

HOW DOES IT WORK?
Step 1: Initialize or setup
Step 2: Execute the logic
Step 3: Get the result
Step 4: Apply it in your code

SIMPLE ANALOGY
{analogy[:100] if analogy else 'Think of ' + name + ' as a building block'}...

WHERE IS IT USED?
Web Development
Mobile Apps
Data Science
Game Development
System Programming

KEY POINTS
Main concept: {name}
Most important: Correct usage
Common mistake: Not following best practices
Real example: Everyday programming task

ADVANTAGES
Easy to use
Improves quality
Best practice
Industry standard

DISADVANTAGES
Takes time to learn
Some edge cases
Needs practice
Version differences"""

    return visual


def regenerate_content_only_visuals():
    """Regenerate all visual explanations with content only"""
    
    print("\n" + "="*70)
    print("CONTENT-ONLY VISUAL EXPLANATION GENERATION")
    print("="*70)
    print("\nStyle: Plain text content only - NO formatting lines or boxes")
    
    topics = list(db.topics.find())
    total = len(topics)
    updated = 0
    
    for i, topic in enumerate(topics, 1):
        try:
            # Generate content-only visual
            content_visual = generate_content_only_visual(topic)
            
            # Update in database
            db.topics.update_one(
                {'_id': topic['_id']},
                {
                    '$set': {
                        'explanations.visual': content_visual
                    }
                }
            )
            
            updated += 1
            
            # Progress every 20 topics
            if i % 20 == 0:
                size = len(content_visual)
                print(f"[{i}/{total}] {topic.get('name', 'Unknown')}")
                print(f"         → Size: {size} chars")
            
        except Exception as e:
            print(f"ERROR at topic {i}: {str(e)}")
    
    print("\n" + "="*70)
    print(f"RESULT: {updated}/{total} visual explanations updated")
    print("="*70)
    print(f"\n✓ All visual explanations now contain:")
    print(f"  • ONLY text content")
    print(f"  • NO box drawings or ASCII art")
    print(f"  • NO decorative lines")
    print(f"  • NO special formatting characters")
    print(f"  • Clean, readable sections")
    print(f"  • Simple headings and content\n")
    
    client.close()

if __name__ == '__main__':
    regenerate_content_only_visuals()
