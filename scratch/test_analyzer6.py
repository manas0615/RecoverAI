from recoverai.llm_gateway.config import GatewayConfig
from recoverai.llm_gateway.providers import GeminiAdapter

config = GatewayConfig.from_env()
gemini = GeminiAdapter(config.gemini_api_key, config.gemini_model)

prompt = "Hello"
schema = {
    "type": "object",
    "properties": {
        "greeting": {"type": "string"}
    }
}

print("Running Gemini...")
try:
    res = gemini.generate_json(prompt, schema)
    print("Raw response:")
    print(res)
except Exception as e:
    import traceback
    traceback.print_exc()

