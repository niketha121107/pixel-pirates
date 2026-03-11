# -*- coding: utf-8 -*-
# Fix all broken dict entries in seed_database.py

with open('seed_database.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: sub-5-1 visual - missing codeExample and closing }
# Line 582: {"style": "visual", ... "content": "...copies indices 1 and 2.",
# Should end with: ...copies indices 1 and 2.", "codeExample": "..."},
content = content.replace(
    '''Slicing creates a NEW list: fruits[1:3] copies indices 1 and 2.",
                    {"style": "analogy", "title": "Analogy"''',
    '''Slicing creates a NEW list: fruits[1:3] copies indices 1 and 2."},
                    {"style": "analogy", "title": "Analogy"'''
)

# Fix 2: sub-5-1 analogy - content missing closing } before codeExample
# Line 583-584: ...one pass.",
#               "codeExample": "..."},
# The "codeExample" on line 584 actually belongs to the analogy dict but the content line doesn't close the dict
content = content.replace(
    '''on a conveyor belt in one pass.",
                    "codeExample": "# Train analogy''',
    '''on a conveyor belt in one pass.", "codeExample": "# Train analogy'''
)

# Fix 3: sub-5-2 visual - same pattern
# Check: ...compact internal array.",
#        {"style": "analogy"...
content = content.replace(
    '''thanks to a compact internal array.",
                    {"style": "analogy", "title": "Analogy", "icon"''',
    '''thanks to a compact internal array."},
                    {"style": "analogy", "title": "Analogy", "icon"'''
)

# Fix 4: sub-5-2 analogy - same pattern
content = content.replace(
    '''that does not exist yet.",
                    "codeExample": "# Filing cabinet''',
    '''that does not exist yet.", "codeExample": "# Filing cabinet'''
)

# Write back
with open('seed_database.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Verify syntax
import ast
try:
    ast.parse(content)
    print("SUCCESS: All syntax errors fixed!")
except SyntaxError as e:
    print(f"Still has error at line {e.lineno}: {e.msg}")
    lines = content.split('\n')
    for i in range(max(0, e.lineno-3), min(len(lines), e.lineno+3)):
        marker = ">>>" if i == e.lineno - 1 else "   "
        print(f"{marker} {i+1}: {lines[i][:150]}")
