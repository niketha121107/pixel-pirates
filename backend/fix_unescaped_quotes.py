# -*- coding: utf-8 -*-
# Fix unescaped quotes inside string values in seed_database.py

import ast
import re

with open('seed_database.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix specific known issue: // "B" should be // \"B\"
# The pattern is: unescaped " inside a Python string
# We know the specific case: // "B" in a Java comment inside a Python string
content = content.replace('// "B"', '// \\"B\\"')

# Also check for any other similar patterns: // "X" where X is short
# Common in code comments showing output
content = content.replace('// "A"', '// \\"A\\"')
content = content.replace('// "C"', '// \\"C\\"')

with open('seed_database.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Verify
try:
    ast.parse(content)
    print("SUCCESS: No syntax errors!")
except SyntaxError as e:
    print(f"Still has error at line {e.lineno}: {e.msg}")
    file_lines = content.split('\n')
    for j in range(max(0, e.lineno-3), min(len(file_lines), e.lineno+3)):
        marker = ">>>" if j == e.lineno - 1 else "   "
        print(f"{marker} {j+1}: {file_lines[j][:200]}")
