# -*- coding: utf-8 -*-
# Comprehensive fix for ALL broken dict patterns in seed_database.py

import ast
import re

with open('seed_database.py', 'r', encoding='utf-8') as f:
    content = f.read()

iteration = 0
max_iterations = 20

while iteration < max_iterations:
    iteration += 1
    lines = content.split('\n')
    fixes = 0
    new_lines = []
    skip_next = False
    
    for i in range(len(lines)):
        if skip_next:
            skip_next = False
            continue
            
        stripped = lines[i].rstrip()
        next_stripped = lines[i+1].strip() if i + 1 < len(lines) else ''
        
        # Pattern 1: Line ends with something", and next line starts {"style":
        # The current dict is missing closing }
        if re.search(r'",\s*$', stripped) and next_stripped.startswith('{"style":'):
            # Check if the current line is inside a list of explanation dicts
            # Replace trailing ", with "},
            new_line = re.sub(r'",\s*$', '"},', stripped)
            new_lines.append(new_line)
            fixes += 1
        # Pattern 2: Line ends with something", and next line starts "codeExample":
        # The codeExample belongs to the current dict but got split to a new line
        elif re.search(r'",\s*$', stripped) and next_stripped.startswith('"codeExample":'):
            # Merge: remove trailing comma, add space, append codeExample line
            current = re.sub(r',\s*$', '', stripped)
            merged = current + ', ' + next_stripped
            new_lines.append(merged)
            skip_next = True
            fixes += 1
        else:
            new_lines.append(lines[i])
    
    content = '\n'.join(new_lines)
    
    if fixes == 0:
        print(f"Iteration {iteration}: No more fixes needed.")
        break
    else:
        print(f"Iteration {iteration}: Applied {fixes} fixes.")

# Write final result
with open('seed_database.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Verify syntax
try:
    ast.parse(content)
    print("\nSUCCESS: No syntax errors!")
except SyntaxError as e:
    print(f"\nStill has error at line {e.lineno}: {e.msg}")
    file_lines = content.split('\n')
    for j in range(max(0, e.lineno-3), min(len(file_lines), e.lineno+3)):
        marker = ">>>" if j == e.lineno - 1 else "   "
        print(f"{marker} {j+1}: {file_lines[j][:200]}")

# Count codeExamples
print(f"\nTotal codeExample occurrences: {content.count('codeExample')}")
