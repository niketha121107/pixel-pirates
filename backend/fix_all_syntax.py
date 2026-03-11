# -*- coding: utf-8 -*-
# Fix ALL broken dict patterns in seed_database.py
# Pattern 1: Missing closing } - visual/analogy content ends with .", but next line starts new {"style":
# Pattern 2: Content and codeExample split across lines (content on one line, codeExample on next)

with open('seed_database.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixes = 0

# Fix Pattern 1: Line ends with .", and next line starts {"style":
# Need to change .", to ."},
i = 0
while i < len(lines) - 1:
    stripped = lines[i].rstrip('\n').rstrip()
    next_stripped = lines[i+1].strip()
    if stripped.endswith('.",') and next_stripped.startswith('{"style":'):
        # Add closing } before the comma
        lines[i] = lines[i].rstrip('\n').rstrip()
        # Replace the last .", with ."},
        lines[i] = lines[i][:-2] + '"},\n'
        fixes += 1
        print(f"  Fix P1 at line {i+1}")
    i += 1

# Fix Pattern 2: Line ends with .", and next line starts with "codeExample":
# Need to merge into one line or make it one dict entry
i = 0
while i < len(lines) - 1:
    stripped = lines[i].rstrip('\n').rstrip()
    next_stripped = lines[i+1].strip()
    if stripped.endswith('.",') and next_stripped.startswith('"codeExample":'):
        # Merge: remove trailing newline from current line, remove leading whitespace from next
        # Current line: ...content text.",
        # Next line:                     "codeExample": "code..."},
        # Result: ...content text.", "codeExample": "code..."},
        current = lines[i].rstrip('\n').rstrip()
        # Remove trailing comma from current
        if current.endswith(','):
            current = current[:-1]
        # Get the codeExample part
        code_part = lines[i+1].strip()
        # Combine: current + ", " + code_part
        indent = '                    '  # standard indent for explanation entries
        lines[i] = current + ' ' + code_part + '\n'
        lines[i+1] = ''  # Remove the now-merged line
        fixes += 1
        print(f"  Fix P2 at line {i+1}")
    i += 1

# Remove empty lines created by merging 
lines = [l for l in lines if l != '']

content = ''.join(lines)

with open('seed_database.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nTotal fixes applied: {fixes}")

# Verify syntax
import ast
try:
    ast.parse(content)
    print("SUCCESS: No more syntax errors!")
except SyntaxError as e:
    print(f"Still has error at line {e.lineno}: {e.msg}")
    file_lines = content.split('\n')
    for j in range(max(0, e.lineno-3), min(len(file_lines), e.lineno+3)):
        marker = ">>>" if j == e.lineno - 1 else "   "
        print(f"{marker} {j+1}: {file_lines[j][:150]}")
