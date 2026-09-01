import json
from recoverai.config import get_settings
from recoverai.llm_gateway.providers import GeminiAdapter, GroqAdapter

settings = get_settings()

print("Gemini Configured:", bool(settings.gemini_api_key))
print("Groq Configured:", bool(settings.groq_api_key))

prompt = "Hello"
schema = {"type": "object", "properties": {"greeting": {"type": "string"}}}

print("\n--- Testing Gemini ---")
gemini = GeminiAdapter(settings.gemini_api_key, settings.gemini_model)
try:
    gemini.generate_json(prompt, schema)
    print("Gemini Succeeded!")
except Exception as e:
    print(f"Gemini Exception: {type(e).__name__}: {e}")

print("\n--- Testing Groq ---")
groq = GroqAdapter(settings.groq_api_key, settings.groq_model)
try:
    groq.generate_json(prompt, schema)
    print("Groq Succeeded!")
except Exception as e:
    print(f"Groq Exception: {type(e).__name__}: {e}")
