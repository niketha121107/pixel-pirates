import re
with open('seed_database.py', 'r', encoding='utf-8') as f:
    c = f.read()
ids = re.findall(r'"id":\s*"(topic-\d+)"', c)
print(f"Total: {len(ids)}")
for t in ids:
    print(t)
