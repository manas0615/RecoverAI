import json
import urllib.error
from unittest.mock import MagicMock, patch

import pytest

from recoverai.llm_gateway.config import GatewayConfig
from recoverai.llm_gateway.engine import ConcreteLLMGateway
from recoverai.llm_gateway.providers import (
    ConfigurationError,
    HuggingFaceAdapter,
    ProviderError,
)


def test_hf_initializes_and_uses_configured_model():
    adapter = HuggingFaceAdapter(api_key="fake-hf-token", model="fake-hf-model")
    assert adapter.api_key == "fake-hf-token"
    assert adapter.model == "fake-hf-model"
    assert adapter.name == "huggingface"


def test_hf_missing_token_raises_configuration_error():
    adapter = HuggingFaceAdapter(api_key=None, model="model")
    with pytest.raises(ConfigurationError, match="Missing Hugging Face API Key"):
        adapter.generate_json("prompt", {})


@patch("urllib.request.urlopen")
def test_hf_successful_request(mock_urlopen):
    adapter = HuggingFaceAdapter(api_key="token", model="model")

    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps(
        {"choices": [{"message": {"content": '{"result": "success"}'}}]}
    ).encode("utf-8")
    mock_response.__enter__.return_value = mock_response
    mock_urlopen.return_value = mock_response

    res = adapter.generate_json("prompt", {})
    assert res == '{"result": "success"}'

    # Verify request payload
    req = mock_urlopen.call_args[0][0]
    assert req.full_url == "https://router.huggingface.co/v1/chat/completions"
    assert req.headers["Authorization"] == "Bearer token"


@patch("urllib.request.urlopen")
def test_hf_authentication_failure(mock_urlopen):
    adapter = HuggingFaceAdapter(api_key="token", model="model")

    mock_urlopen.side_effect = urllib.error.HTTPError(
        url="", code=401, msg="Unauthorized", hdrs={}, fp=MagicMock(read=lambda: b"{}")
    )

    with pytest.raises(
        ConfigurationError, match="Authentication/Configuration failed: 401"
    ):
        adapter.generate_json("prompt", {})


@patch("urllib.request.urlopen")
def test_hf_timeout(mock_urlopen):
    adapter = HuggingFaceAdapter(api_key="token", model="model")

    mock_urlopen.side_effect = TimeoutError("timeout")

    with pytest.raises(
        ProviderError, match="Hugging Face API failed: TimeoutError - timeout"
    ):
        adapter.generate_json("prompt", {})


@patch("urllib.request.urlopen")
def test_hf_503_unavailable(mock_urlopen):
    adapter = HuggingFaceAdapter(api_key="token", model="model")

    mock_urlopen.side_effect = urllib.error.HTTPError(
        url="",
        code=503,
        msg="Service Unavailable",
        hdrs={},
        fp=MagicMock(read=lambda: b"{}"),
    )

    with pytest.raises(ProviderError, match="Hugging Face API failed: 503"):
        adapter.generate_json("prompt", {})


def test_engine_provider_selection():
    config = GatewayConfig(
        gemini_api_key="gem",
        groq_api_key="groq",
        hf_api_key="hf",
        primary_provider="huggingface",
    )
    engine = ConcreteLLMGateway(config)
    assert engine.providers[0].name == "huggingface"
    assert engine.providers[1].name == "gemini" or engine.providers[1].name == "groq"
