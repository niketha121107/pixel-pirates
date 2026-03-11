# -*- coding: utf-8 -*-
# Fix syntax errors in seed_database.py - missing closing braces on dict entries
import re

with open('seed_database.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: sub-5-1 visual explanation - missing closing }
# Line has: ...copies indices 1 and 2.",
# Should be: ...copies indices 1 and 2."},
content = content.replace(
    'Slicing creates a NEW list: fruits[1:3] copies indices 1 and 2.",\n                    {"style": "analogy"',
    'Slicing creates a NEW list: fruits[1:3] copies indices 1 and 2."},\n                    {"style": "analogy"'
)

# Fix 2: sub-5-1 analogy explanation - missing closing }
# Line has: ...on a conveyor belt in one pass.",
# Should be: ...on a conveyor belt in one pass."},
content = content.replace(
    'processing each item on a conveyor belt in one pass.",\n                    "codeExample": "# Train analogy',
    'processing each item on a conveyor belt in one pass."},\n                    {"style": "analogy", "title": "Analogy", "icon": "\ud83d\udd17", "content": "A list is like a train with numbered carriages. Each carriage (index) can hold a different type of cargo: numbers, strings, even other trains (nested lists). Appending is like coupling a new carriage at the end, which is quick. Inserting in the middle is like adding a carriage between existing ones: every carriage behind it must shuffle back, which takes more work. Slicing is like detaching a section of carriages to form a brand-new mini-train. A list comprehension is like an automated factory that builds a new train by processing each item on a conveyor belt in one pass.", "codeExample": "# Train analogy'
)

# Wait, let me re-check - the analogy dict is actually split across two lines incorrectly. 
# Let me look at this differently...

# Actually, the pattern is:
# Line 582: visual entry ends with ...indices 1 and 2.", (MISSING closing })
# Line 583: analogy entry starts with {"style": ... but content ends with ...one pass.",
# Line 584: "codeExample": ... (this is meant to be part of the analogy dict)
# Line 585: ],  (closing the explanations list)

# So the fix is simpler: just add } before the comma on the visual line
# and ensure the analogy dict is properly formed

print("Attempting fixes...")

# Let me check by trying to find the exact strings
idx1 = content.find('copies indices 1 and 2.",')
print(f"Fix 1 at pos: {idx1}")
if idx1 != -1:
    print(f"Context: {repr(content[idx1:idx1+60])}")

idx2 = content.find('on a conveyor belt in one pass.",')
print(f"Fix 2 at pos: {idx2}")
if idx2 != -1:
    print(f"Context: {repr(content[idx2:idx2+80])}")

# Also check sub-5-2 for similar issues
idx3 = content.find('thanks to a compact internal array.",')
print(f"Fix 3 (sub-5-2 visual) at pos: {idx3}")
if idx3 != -1:
    print(f"Context: {repr(content[idx3:idx3+60])}")

idx4 = content.find('that does not exist yet.",')
print(f"Fix 4 (sub-5-2 analogy) at pos: {idx4}")
if idx4 != -1:
    print(f"Context: {repr(content[idx4:idx4+80])}")
