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
