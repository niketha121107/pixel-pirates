# Inspect TOPICS structure for surrogate code points after Python parses literals

import seed_database


def has_surrogate(s: str) -> bool:
    return any(0xD800 <= ord(c) <= 0xDFFF for c in s)


def walk(obj, path='root'):
    if isinstance(obj, str):
        if has_surrogate(obj):
            print(f'SURROGATE at {path}: {obj.encode("unicode_escape")[:200]}')
            return 1
        return 0
    if isinstance(obj, dict):
        c = 0
        for k, v in obj.items():
            c += walk(v, f"{path}.{k}")
        return c
    if isinstance(obj, list):
        c = 0
        for i, v in enumerate(obj):
            c += walk(v, f"{path}[{i}]")
        return c
    return 0

count = walk(seed_database.TOPICS, 'TOPICS')
print('Total surrogate-containing strings:', count)
