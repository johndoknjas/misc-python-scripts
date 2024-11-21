import sys

lines: str = """
"""
# replace with your lines

def leading_spaces(s: str) -> int:
    return len(s) - len(s.lstrip(' '))

def bad_line(l: str) -> bool:
    return any(x in l for x in '{}()=>|*') or leading_spaces(l) < 3

lines = lines.split('\n')
for i, first in enumerate(lines):
    if i >= len(lines) - 2:
        sys.exit(0)
    second = lines[i+2]
    if bad_line(first) or bad_line(second) or leading_spaces(first) != leading_spaces(second):
        continue
    if first.strip().lower() > second.strip().lower():
        print(first, second)