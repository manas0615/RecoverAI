import urllib.request
import json
from recoverai.config import settings

model = "qwen/qwen3.6-27b"
print(f"Testing {model}...")
req = urllib.request.Request(
    "https://api.groq.com/openai/v1/chat/completions",
    data=json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": "Return JSON: {\"ok\": true}"}],
    }).encode(),
    headers={
        "Authorization": f"Bearer {settings.groq_api_key}", 
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
)
try:
    with urllib.request.urlopen(req) as resp:
        print(resp.read().decode())
except Exception as e:
    print(e.read().decode())
