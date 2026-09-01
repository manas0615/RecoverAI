from recoverai.llm_gateway.config import GatewayConfig
from recoverai.llm_gateway.providers import GeminiAdapter

config = GatewayConfig.from_env()
gemini = GeminiAdapter(config.gemini_api_key, config.gemini_model)

prompt = "Hello"
schema = {
    "type": "object",
    "properties": {
        "candidates": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "action_type": {"type": "string"},
                    "confidence": {"type": "number"},
                    "confidence_meaning": {"type": "string"},
                    "reasoning": {"type": "string"},
                    "evidence_references": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {"source_id": {"type": "string"}},
                            "required": ["source_id"],
                        },
                    },
                },
                "required": [
                    "action_type",
                    "confidence",
                    "reasoning",
                    "evidence_references",
                ],
            },
        }
    },
    "required": ["candidates"],
}

print("Running Gemini...")
res = gemini.generate_json(prompt, schema)
print("Raw response:")
print(res)

from recoverai.llm_gateway.schemas import InterventionPlanResponseModel
print("\nParsing...")
try:
    plan = InterventionPlanResponseModel.model_validate_json(res)
    print("Parsed plan successfully:", plan)
except Exception as e:
    print(f"Failed to parse: {e}")

