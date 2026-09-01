import urllib.request
import json
from recoverai.config import settings

req = urllib.request.Request(
    "https://api.groq.com/openai/v1/chat/completions",
    data=json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": "hi"}],
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
