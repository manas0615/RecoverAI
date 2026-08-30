from recoverai.llm_gateway.config import GatewayConfig


def test_config_from_env(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "gemini_secret")
    monkeypatch.setenv("GROQ_API_KEY", "groq_secret")
    monkeypatch.setenv("HF_API_KEY", "hf_secret")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-test")
    monkeypatch.setenv("GROQ_MODEL", "groq-test")
    monkeypatch.setenv("HF_MODEL", "hf-test")

    config = GatewayConfig.from_env()
    assert config.gemini_api_key == "gemini_secret"
    assert config.groq_api_key == "groq_secret"
    assert config.hf_api_key == "hf_secret"
    assert config.gemini_model == "gemini-test"
    assert config.groq_model == "groq-test"
    assert config.hf_model == "hf-test"


def test_config_missing_credentials(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    config = GatewayConfig.from_env()
    assert config.gemini_api_key is None
    # defaults
    assert config.gemini_model == "gemini-3.6-flash"
