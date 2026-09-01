import urllib.request
import json
from recoverai.config import settings

for model in ["llama3-8b-8192", "llama3-70b-8192", "llama-3.1-70b-versatile", "llama-3.1-8b-instant", "llama-3.2-3b-preview"]:
    print(f"Testing {model}...")
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps({
            "model": model,
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
