import os
from dataclasses import dataclass


@dataclass
class GatewayConfig:
    gemini_api_key: str | None = None
    groq_api_key: str | None = None
    hf_api_key: str | None = None
    gemini_model: str = "gemini-2.5-pro"
    groq_model: str = "llama3-70b-8192"
    hf_model: str = "meta-llama/Llama-3-70b-chat-hf"

    @classmethod
    def from_env(cls) -> "GatewayConfig":
        return cls(
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            groq_api_key=os.getenv("GROQ_API_KEY"),
            hf_api_key=os.getenv("HF_API_KEY"),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-pro"),
            groq_model=os.getenv("GROQ_MODEL", "llama3-70b-8192"),
            hf_model=os.getenv("HF_MODEL", "meta-llama/Llama-3-70b-chat-hf"),
        )
