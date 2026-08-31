with open('recoverai/api/main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'funnel["ANALYZED"]' in line:
        for j in range(i, i+25):
            if j < len(lines):
                print(lines[j], end='')
        break
