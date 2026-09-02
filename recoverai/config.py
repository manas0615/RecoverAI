from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings for RecoverAI.
    Loads from environment variables or a .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Razorpay Configuration (Placeholders)
    razorpay_mode: str = Field(
        default="test", description="Razorpay mode: 'test' or 'live'"
    )
    razorpay_key_id: str | None = Field(default=None, description="Razorpay API Key ID")
    razorpay_key_secret: str | None = Field(
        default=None, description="Razorpay API Key Secret"
    )
    razorpay_webhook_secret: str | None = Field(
        default=None, description="Razorpay Webhook Secret"
    )

    # AI Providers Configuration (Placeholders)
    llm_provider: str = Field(default="gemini", description="Primary LLM Provider")
    gemini_api_key: str | None = Field(default=None, description="Gemini API Key")
    groq_api_key: str | None = Field(default=None, description="Groq API Key")
    hf_token: str | None = Field(default=None, description="Hugging Face Token")

    # Infrastructure Configuration (Placeholders)
    database_url: str = Field(
        default="sqlite:///recoverai.db", description="Database URL"
    )

    # n8n Orchestration (Placeholders)
    n8n_base_url: str | None = Field(default=None, description="n8n Base URL")
    n8n_api_token: str | None = Field(default=None, description="n8n API Token")

    # Security & API Boundaries
    frontend_api_key: str = Field(
        default="test_frontend_key_default",
        description="Lightweight client credential for frontend reads",
    )
    n8n_api_key: str = Field(
        default="test_n8n_key_default",
        description="Server-side secret for n8n orchestrator access to MCP",
    )
    frontend_cors_origin: str = Field(
        default="http://localhost:5173",
        description="Allowed CORS origin for the frontend",
    )

    # Application Settings
    log_level: str = Field(default="INFO", description="Logging level")
    environment: str = Field(
        default="development",
        description="Current environment (development, test, production)",
    )


def get_settings() -> Settings:
    """
    Returns the application settings instance.
    Handles configuration errors by raising ValueError if required settings are missing.
    """
    try:
        return Settings()
    except Exception as e:  # noqa: BLE001
        # We do not log the full exception here to avoid leaking secrets that might be in the environment
        raise ValueError(f"Failed to load application configuration: {e!s}")


# Global settings instance for early bootstrap if needed, though dependency injection is preferred later.
settings = get_settings()
