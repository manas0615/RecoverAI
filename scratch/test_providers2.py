import json
from recoverai.llm_gateway.config import GatewayConfig
from recoverai.llm_gateway.providers import GeminiAdapter, GroqAdapter

config = GatewayConfig.from_env()

print("Gemini Configured:", bool(config.gemini_api_key))
print("Groq Configured:", bool(config.groq_api_key))

prompt = "Hello"
schema = {"type": "object", "properties": {"greeting": {"type": "string"}}}

print("\n--- Testing Gemini ---")
gemini = GeminiAdapter(config.gemini_api_key, config.gemini_model)
try:
    gemini.generate_json(prompt, schema)
    print("Gemini Succeeded!")
except Exception as e:
    print(f"Gemini Exception: {type(e).__name__}: {e}")

print("\n--- Testing Groq ---")
groq = GroqAdapter(config.groq_api_key, config.groq_model)
try:
    groq.generate_json(prompt, schema)
    print("Groq Succeeded!")
except Exception as e:
    print(f"Groq Exception: {type(e).__name__}: {e}")
