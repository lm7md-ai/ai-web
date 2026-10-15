"""Pluggable LLM providers.

The platform must work with **no** provider configured: every caller degrades
to the deterministic heuristics in :mod:`pfn.ai.mentor` when `is_enabled()` is
false, and the UI must say so rather than pretending otherwise.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field


@dataclass(slots=True)
class Message:
    role: str  # system | user | assistant
    content: str

    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.content}


@dataclass(slots=True)
class Completion:
    text: str
    model: str
    provider: str
    raw: dict = field(default_factory=dict)
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None

    def json(self) -> dict | None:
        """Best-effort extraction of a JSON object from the reply."""
        text = self.text.strip()
        fence = re.search(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", text, re.DOTALL)
        candidate = fence.group(1) if fence else text[text.find("{"): text.rfind("}") + 1]
        try:
            return json.loads(candidate)
        except (ValueError, TypeError):
            return None


class Provider:
    """Common behaviour for HTTP chat-completion providers."""

    name = "base"
    default_model = ""
    default_base_url = ""
    env_key = ""

    def __init__(self, api_key: str | None = None, model: str | None = None,
                 base_url: str | None = None, timeout: float = 30.0) -> None:
        self.api_key = api_key or os.environ.get(self.env_key) or ""
        self.model = model or os.environ.get(f"{self.name.upper()}_MODEL") or self.default_model
        self.base_url = (base_url or os.environ.get(f"{self.name.upper()}_BASE_URL")
                         or self.default_base_url).rstrip("/")
        self.timeout = timeout

    def is_enabled(self) -> bool:
        return bool(self.api_key and self.base_url and self.model)

    def endpoint(self) -> str:
        return f"{self.base_url}/chat/completions"

    def payload(self, messages: list[Message], temperature: float, max_tokens: int) -> dict:
        return {
            "model": self.model,
            "messages": [message.to_dict() for message in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }

    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def parse(self, data: dict) -> str:
        choices = data.get("choices") or []
        if not choices:
            return ""
        message = choices[0].get("message") or {}
        return message.get("content") or ""

    def complete(self, messages: list[Message], temperature: float = 0.3,
                 max_tokens: int = 1200) -> Completion:
        if not self.is_enabled():
            return Completion("", self.model, self.name, error="provider not configured")
        body = json.dumps(self.payload(messages, temperature, max_tokens)).encode("utf-8")
        request = urllib.request.Request(self.endpoint(), data=body, headers=self.headers(), method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", "replace")[:400]
            return Completion("", self.model, self.name, error=f"HTTP {error.code}: {detail}")
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            return Completion("", self.model, self.name, error=f"network error: {error}")
        except ValueError as error:
            return Completion("", self.model, self.name, error=f"bad JSON: {error}")
        return Completion(self.parse(data), self.model, self.name, raw=data)


class OpenAICompatibleProvider(Provider):
    name = "openai"
    default_model = "gpt-4o-mini"
    default_base_url = "https://api.openai.com/v1"
    env_key = "OPENAI_API_KEY"


class OllamaProvider(Provider):
    """Local Ollama server - no API key required."""

    name = "ollama"
    default_model = "llama3.2:3b"
    default_base_url = "http://localhost:11434/v1"
    env_key = "OLLAMA_API_KEY"

    def is_enabled(self) -> bool:
        return bool(self.base_url and self.model)

    def headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers


PROVIDERS: dict[str, type[Provider]] = {
    "openai": OpenAICompatibleProvider,
    "ollama": OllamaProvider,
}


def build_provider(name: str | None = None, **kwargs) -> Provider:
    selected = (name or os.environ.get("PFN_AI_PROVIDER") or "").strip().lower()
    cls = PROVIDERS.get(selected)
    if cls is None:
        cls = Provider  # disabled placeholder so callers never break
    return cls(**kwargs)
