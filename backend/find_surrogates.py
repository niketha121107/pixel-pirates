# Find invalid surrogate characters in seed_database.py

from pathlib import Path

p = Path('seed_database.py')
text = p.read_text(encoding='utf-8')

found = []
for i, ch in enumerate(text):
    o = ord(ch)
    if 0xD800 <= o <= 0xDFFF:
        found.append((i, o))

print(f"Total surrogate chars: {len(found)}")
if found:
    line = 1
    col = 1
    idx_map = {}
    j = 0
    for pos, ch in enumerate(text):
        if j < len(found) and pos == found[j][0]:
            idx_map[pos] = (line, col, found[j][1])
            j += 1
        if ch == '\n':
            line += 1
            col = 1
        else:
            col += 1

    for pos, code in found[:200]:
        ln, cl, oc = idx_map[pos]
        snippet = text[max(0, pos-30):pos+30].replace('\n', '\\n')
        print(f"line {ln}, col {cl}, code U+{oc:04X}, snippet: {snippet}")
