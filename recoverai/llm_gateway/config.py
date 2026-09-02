import os
from dataclasses import dataclass


@dataclass
class GatewayConfig:
    gemini_api_key: str | None = None
    groq_api_key: str | None = None
    hf_api_key: str | None = None
    gemini_model: str = "gemini-3.6-flash"
    groq_model: str = "llama-3.3-70b-versatile"
    hf_model: str = "meta-llama/Llama-3.3-70B-Instruct"
    primary_provider: str = "gemini"

    @classmethod
    def from_env(cls) -> "GatewayConfig":
        from recoverai.config import settings

        return cls(
            gemini_api_key=os.getenv("GEMINI_API_KEY") or settings.gemini_api_key,
            groq_api_key=os.getenv("GROQ_API_KEY") or settings.groq_api_key,
            hf_api_key=os.getenv("HF_TOKEN") or settings.hf_token,
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
            groq_model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            hf_model=os.getenv("HF_MODEL", "meta-llama/Llama-3.3-70B-Instruct"),
            primary_provider=os.getenv("LLM_PROVIDER") or settings.llm_provider,
        )
