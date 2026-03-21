#!/usr/bin/env python3
"""Check visual explanations for all topics and identify any that need improvement"""
from app.data import get_all_topics, initialize_data
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize data
initialize_data()
topics = get_all_topics()

print("=" * 80)
print("VISUAL EXPLANATION QUALITY CHECK")
print("=" * 80)

excellent = []  # 4000+ chars
good = []       # 2000-3999 chars
fair = []       # 500-1999 chars
poor = []       # <500 chars
empty = []      # no visual

for topic in topics:
    name = topic.get("name", "Unknown")
    lang = topic.get("language", "Unknown")
    visual = topic.get("explanations", {}).get("visual", "")
    
    length = len(visual) if visual else 0
    
    if length == 0:
        empty.append((name, lang))
    elif length < 500:
        poor.append((name, lang, length))
    elif length < 2000:
        fair.append((name, lang, length))
    elif length < 4000:
        good.append((name, lang, length))
    else:
        excellent.append((name, lang, length))

print(f"\n✓ EXCELLENT (4000+ chars):    {len(excellent)} topics")
print(f"✓ GOOD (2000-3999 chars):     {len(good)} topics")
print(f"⚠ FAIR (500-1999 chars):      {len(fair)} topics")
print(f"✗ POOR (<500 chars):          {len(poor)} topics")
print(f"✗ EMPTY (no visual):          {len(empty)} topics")

total = len(excellent) + len(good) + len(fair) + len(poor) + len(empty)
print(f"\nTotal: {total}/200 topics checked")

if empty or poor:
    print("\n" + "=" * 80)
    print("TOPICS NEEDING IMPROVEMENT:")
    print("=" * 80)
    
    if empty:
        print(f"\nEMPTY VISUAL ({len(empty)} topics):")
        for name, lang in empty[:10]:
            print(f"  - {name} ({lang})")
        if len(empty) > 10:
            print(f"  ... and {len(empty) - 10} more")
    
    if poor:
        print(f"\nPOOR VISUAL (<500 chars, {len(poor)} topics):")
        for name, lang, length in poor[:10]:
            print(f"  - {name} ({lang}) - {length} chars")
        if len(poor) > 10:
            print(f"  ... and {len(poor) - 10} more")

print("\n" + "=" * 80)
print(f"OVERALL QUALITY: {len(excellent) + len(good)}/200 topics with substantial visual explanations")
print("=" * 80)
