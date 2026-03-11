# -*- coding: utf-8 -*-
# Fix all syntax errors in seed_database.py

with open('seed_database.py', 'r', encoding='utf-8') as f:
    content = f.read()

fixes = 0

# Fix 1: sub-5-1 analogy - content and codeExample are separated into 2 dicts
# Pattern: ...one pass.", "codeExample": ... (missing } between content and the NEXT entry)
# Actually this means the analogy dict is split: content ends then codeExample starts on new line
# The real issue: the visual dict content ends without }, then analogy starts without having its own }

# Let me find ALL places where a pattern like: 
# .", "codeExample": 
# appears (meaning codeExample is separated from style/title/icon/content)
import re

# Pattern: content string ends, then directly "codeExample" key appears in same dict
# This is VALID if it's all inside one {} dict
# Let me instead just find where a dict entry is missing closing }

# Better approach: find "codeExample" preceded by newline (meaning it's a separate line from the dict start)
# These are cases where the dict was split incorrectly

# Fix sub-5-1 analogy: 
# Old: ...one pass.", 
#     "codeExample": "# Train..."},
# Should be: ...one pass.", "codeExample": "# Train..."},
# Wait, from the output it's actually: ...one pass.", "codeExample": ... which is correct dict syntax
# Let me re-read the file more carefully

# Let me just find all issues using Python's compile  
import ast
try:
    ast.parse(content)
    print("No syntax errors!")
except SyntaxError as e:
    print(f"Syntax error at line {e.lineno}: {e.msg}")
    # Show the problematic lines
    lines = content.split('\n')
    for i in range(max(0, e.lineno-3), min(len(lines), e.lineno+3)):
        marker = ">>>" if i == e.lineno - 1 else "   "
        print(f"{marker} {i+1}: {lines[i][:120]}")
