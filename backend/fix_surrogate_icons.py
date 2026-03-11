# Replace surrogate-escape icon literals with ASCII-safe icons

from pathlib import Path
import ast

p = Path('seed_database.py')
text = p.read_text(encoding='utf-8')

replacements = {
    '"icon": "\\ud83d\\udcdd"': '"icon": "[NOTE]"',
    '"icon": "\\ud83e\\udde0"': '"icon": "[LOGIC]"',
    '"icon": "\\ud83c\\udfa8"': '"icon": "[VISUAL]"',
    '"icon": "\\ud83d\\udd17"': '"icon": "[ANALOGY]"',
}

count = 0
for old, new in replacements.items():
    n = text.count(old)
    if n:
        text = text.replace(old, new)
        count += n

p.write_text(text, encoding='utf-8')
print(f'Replaced icon literals: {count}')

ast.parse(text)
print('Syntax OK')
