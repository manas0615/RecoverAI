import requests
res = requests.get('http://127.0.0.1:8000/openapi.json')
paths = res.json().get('paths', {}).keys()
for p in paths: print(p)
