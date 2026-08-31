import re

with open('recoverai/api/main.py') as f:
    content = f.read()

# Find non-existent attribute accesses
patterns = ['case.id', 'case.provenance', 'case.rules_matched', 'action.strategy_type', 'action.executed_at']
for pat in patterns:
    matches = [(i+1, line.strip()) for i, line in enumerate(content.splitlines()) if pat in line]
    if matches:
        print(f"\n=== {pat} ===")
        for lineno, line in matches:
            print(f"  L{lineno}: {line}")
