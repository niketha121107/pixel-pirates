# -*- coding: utf-8 -*-
# Find ALL broken dict patterns in seed_database.py

with open('seed_database.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Pattern 1: Line ends with .", and next line starts a NEW dict {"style": 
# This means the current dict is missing closing }
print("=== Pattern 1: Missing } before next dict entry ===")
for i, line in enumerate(lines):
    stripped = line.rstrip()
    if stripped.endswith('.",') and i + 1 < len(lines):
        next_stripped = lines[i+1].strip()
        if next_stripped.startswith('{"style":'):
            print(f"Line {i+1}: ...{stripped[-60:]}")

# Pattern 2: Line ends with .", and next line starts with "codeExample":
# This means content and codeExample are on separate lines (should be in same dict)
print("\n=== Pattern 2: Split dict (content then codeExample on next line) ===")
for i, line in enumerate(lines):
    stripped = line.rstrip()
    if stripped.endswith('.",') and i + 1 < len(lines):
        next_stripped = lines[i+1].strip()
        if next_stripped.startswith('"codeExample":'):
            print(f"Line {i+1}: ...{stripped[-60:]}")
