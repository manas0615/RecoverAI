import urllib.request
import json
from recoverai.config import settings

for model in ["llama-3.3-70b-specdec", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"]:
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
            print("SUCCESS")
    except Exception as e:
        print(e.read().decode())
