import json
import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class ProviderError(Exception):
    pass


class ProviderAdapter(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def generate_json(self, prompt: str, schema: dict[str, Any]) -> str:
        pass


class MockProvider(ProviderAdapter):
    def __init__(
        self, name: str, canned_responses: list[str] | None = None, fail_count: int = 0
    ):
        self._name = name
        self.canned_responses = canned_responses or []
        self.fail_count = fail_count
        self.calls = 0

    @property
    def name(self) -> str:
        return self._name

    def generate_json(self, prompt: str, schema: dict[str, Any]) -> str:
        self.calls += 1
        if self.fail_count > 0:
            self.fail_count -= 1
            raise ProviderError(f"{self.name} simulated failure")
        if not self.canned_responses:
            raise ProviderError("No canned responses left")
        return self.canned_responses.pop(0)


class GeminiAdapter(ProviderAdapter):
    def __init__(self, api_key: str | None, model: str):
        self.api_key = api_key
        self.model = model

    @property
    def name(self) -> str:
        return "gemini"

    def generate_json(self, prompt: str, schema: dict[str, Any]) -> str:
        if not self.api_key:
            raise ProviderError("Missing Gemini API Key")
        # In a real implementation, we would make a urllib request to api.gemini.com
        # For the buildathon/MVP, real SDKs are banned/mocked in tests.
        # So we just raise unimplemented if this is actually hit in non-mock env without an intercept.
        import urllib.error
        import urllib.request

        # Minimal skeleton for HTTP to prove architecture
        req = urllib.request.Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}",
            data=json.dumps(
                {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "responseMimeType": "application/json",
                        "responseSchema": schema,
                    },
                }
            ).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode())
                return result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            raise ProviderError(f"Gemini API failed: {e}") from e


class GroqAdapter(ProviderAdapter):
    def __init__(self, api_key: str | None, model: str):
        self.api_key = api_key
        self.model = model

    @property
    def name(self) -> str:
        return "groq"

    def generate_json(self, prompt: str, schema: dict[str, Any]) -> str:
        if not self.api_key:
            raise ProviderError("Missing Groq API Key")
        import urllib.request

        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=json.dumps(
                {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"},
                }
            ).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode())
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            raise ProviderError(f"Groq API failed: {e}") from e


class HuggingFaceAdapter(ProviderAdapter):
    def __init__(self, api_key: str | None, model: str):
        self.api_key = api_key
        self.model = model

    @property
    def name(self) -> str:
        return "huggingface"

    def generate_json(self, prompt: str, schema: dict[str, Any]) -> str:
        if not self.api_key:
            raise ProviderError("Missing Hugging Face API Key")
        import urllib.request

        req = urllib.request.Request(
            "https://api-inference.huggingface.co/models/"
            + self.model
            + "/v1/chat/completions",
            data=json.dumps(
                {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"},
                }
            ).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode())
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            raise ProviderError(f"Hugging Face API failed: {e}") from e
