#!/usr/bin/env python3
"""Check for any topics with missing or empty visual explanations"""
from app.data import get_all_topics

topics = get_all_topics()
print("Checking visual explanations across all 200 topics...\n")

missing_visual = []
short_visual = []

for topic in topics:
    explanations = topic.get("explanations", {})
    visual = explanations.get("visual", "")
    
    if not visual:
        missing_visual.append((topic.get("name"), topic.get("language"), topic.get("id")))
    elif len(visual) < 500:
        short_visual.append((topic.get("name"), topic.get("language"), len(visual)))

print(f"Topics with MISSING visual explanation: {len(missing_visual)}")
if missing_visual:
    for name, lang, topic_id in missing_visual[:5]:
        print(f"  - {name} ({lang}) - ID: {topic_id}")

print(f"\nTopics with SHORT visual explanation (<500 chars): {len(short_visual)}")
if short_visual:
    for name, lang, length in short_visual[:5]:
        print(f"  - {name} ({lang}) - {length} chars")

if not missing_visual and not short_visual:
    print("\n✅ All visual explanations present and substantial!")
