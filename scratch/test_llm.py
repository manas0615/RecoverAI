import logging
from recoverai.llm_gateway.config import GatewayConfig
from recoverai.llm_gateway.engine import ConcreteLLMGateway

logging.basicConfig(level=logging.DEBUG)

config = GatewayConfig.from_env()
print("Gemini Key length:", len(config.gemini_api_key) if config.gemini_api_key else 0)
print("Groq Key length:", len(config.groq_api_key) if config.groq_api_key else 0)

gateway = ConcreteLLMGateway(config)
for p in gateway.providers:
    print(f"Provider: {p.name}, initialized with model {p.model}")
