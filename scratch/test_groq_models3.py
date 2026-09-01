import urllib.request
import json
from recoverai.config import settings

req = urllib.request.Request(
    "https://api.groq.com/openai/v1/models",
    headers={
        "Authorization": f"Bearer {settings.groq_api_key}",
        "User-Agent": "Mozilla/5.0"
    }
)
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print(json.dumps(data, indent=2))
except Exception as e:
    print(e.read().decode())
