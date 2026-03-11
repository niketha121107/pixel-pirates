# -*- coding: utf-8 -*-
# Fix missing commas between "content" and "codeExample" in multi-line dict entries

import ast
import re

with open('seed_database.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern: ..." "codeExample": should be ...", "codeExample":
# This happens when content and codeExample were merged but without a comma
fixes = 0
# Find pattern: some text ending quotes followed by space then "codeExample"
# e.g.: ...matrices." "codeExample": 
content_new = re.sub(
    r'" "codeExample":', 
    '", "codeExample":', 
    content
)
fixes = content.count('" "codeExample":') - content_new.count('" "codeExample":')
content = content_new
print(f"Fixed {fixes} missing commas between content and codeExample")

with open('seed_database.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Verify
try:
    ast.parse(content)
    print("\nSUCCESS: No syntax errors!")
except SyntaxError as e:
    print(f"\nStill has error at line {e.lineno}: {e.msg}")
    file_lines = content.split('\n')
    for j in range(max(0, e.lineno-3), min(len(file_lines), e.lineno+3)):
        marker = ">>>" if j == e.lineno - 1 else "   "
        print(f"{marker} {j+1}: {file_lines[j][:200]}")

print(f"\nTotal codeExample occurrences: {content.count('codeExample')}")
