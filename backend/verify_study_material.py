#!/usr/bin/env python3
"""Verify study_material field in MongoDB"""
from app.data import get_all_topics

topics = get_all_topics()
print(f"Total topics: {len(topics)}")
print()

# Find Python Syntax topic
target_topic = None
for topic in topics:
    if "Syntax" in topic.get("name", "") and topic.get("language") == "Python":
        target_topic = topic
        break

if target_topic:
    name = target_topic.get("name", "Unknown")
    lang = target_topic.get("language", "Unknown")
    print(f"Found: {name} ({lang})")
    print(f"Keys in topic: {list(target_topic.keys())}")
    print()
    
    sm = target_topic.get("study_material")
    if sm:
        print("✅ study_material field EXISTS!")
        print(f"Type: {type(sm).__name__}")
        if isinstance(sm, dict):
            print(f"Keys in study_material: {list(sm.keys())}")
            for k in sm.keys():
                v = sm[k]
                if isinstance(v, str):
                    print(f"  {k}: {len(v)} chars")
                else:
                    print(f"  {k}: {type(v).__name__}")
        else:
            print(f"Value (first 100 chars): {str(sm)[:100]}")
    else:
        print("❌ study_material field NOT FOUND")
        study_related = [k for k in target_topic.keys() if "study" in k.lower() or "material" in k.lower()]
        print(f"Fields related to study: {study_related if study_related else 'None'}")
        print()
        print("Available fields:")
        for k in sorted(target_topic.keys()):
            v = target_topic[k]
            if isinstance(v, str):
                print(f"  {k}: {len(v)} chars")
            elif isinstance(v, dict):
                print(f"  {k}: dict with {len(v)} keys")
            elif isinstance(v, list):
                print(f"  {k}: list with {len(v)} items")
            else:
                print(f"  {k}: {type(v).__name__}")
else:
    print("❌ Python Syntax topic not found")
