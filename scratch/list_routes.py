import re

with open('recoverai/api/main.py') as f:
    content = f.read()

routes = re.findall(r'@app\.(get|post|put|patch|delete)\("([^"]+)"', content)
for method, path in routes:
    print(method.upper(), path)
