# -*- coding: utf-8 -*-
# Iteratively fix ALL broken dict patterns in seed_database.py

import ast

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
        
        if stripped.endswith('.",') and next_stripped.startswith('{"style":'):
            # Pattern 1: Missing closing } - add it
            new_lines.append(stripped[:-2] + '"},')
            fixes += 1
        elif stripped.endswith('.",') and next_stripped.startswith('"codeExample":'):
            # Pattern 2: Split dict - merge lines
            current = stripped.rstrip(',')
            merged = current + ' ' + next_stripped
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
