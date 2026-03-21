#!/usr/bin/env python3
"""Find the topic ID for Python Syntax"""
from app.data import get_all_topics

topics = get_all_topics()
print(f"Total topics: {len(topics)}")

# Find Python Syntax topic
for topic in topics:
    if "Syntax" in topic.get("name", "") and topic.get("language") == "Python":
        topic_id = topic.get("id")
        print(f"\nFound topic:")
        print(f"  ID: {topic_id}")
        print(f"  Name: {topic.get('name')}")
        print(f"  Language: {topic.get('language')}")
        break
