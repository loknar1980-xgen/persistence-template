"""Shared LLM API client for persistence-template tools.

Supports LM Studio (default, OpenAI-compatible) and Claude API.
Uses only Python stdlib — no pip install required.

Configuration via environment variables:
    PERSISTENCE_LLM_URL   — API endpoint (default: http://localhost:1234/v1)
    PERSISTENCE_LLM_KEY   — API key (default: lm-studio for LM Studio)
    PERSISTENCE_LLM_MODEL — Model identifier (default: auto-detect loaded model)
"""

import json
import os
import urllib.request
import urllib.error


class LLMClient:
    """Unified client for LM Studio and Claude API."""

    def __init__(self, api_url=None, api_key=None, model=None):
        self.api_url = api_url or os.environ.get(
            "PERSISTENCE_LLM_URL", "http://localhost:1234/v1"
        )
        self.api_key = api_key or os.environ.get(
            "PERSISTENCE_LLM_KEY", "lm-studio"
        )
        self.model = model or os.environ.get("PERSISTENCE_LLM_MODEL", "")
        self.is_claude = "anthropic.com" in self.api_url

    def chat(self, messages, max_tokens=1024, temperature=0.7):
        """Send a chat completion request. Returns the response text."""
        if self.is_claude:
            return self._chat_claude(messages, max_tokens, temperature)
        return self._chat_openai(messages, max_tokens, temperature)

    def _chat_openai(self, messages, max_tokens, temperature):
        """OpenAI-compatible API (LM Studio, Ollama, etc.)."""
        url = f"{self.api_url.rstrip('/')}/chat/completions"
        model = self.model or self._detect_model()

        payload = json.dumps({
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )

        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        return data["choices"][0]["message"]["content"]

    def _chat_claude(self, messages, max_tokens, temperature):
        """Anthropic Claude API."""
        url = f"{self.api_url.rstrip('/')}/messages"

        system_msg = None
        chat_msgs = []
        for m in messages:
            if m["role"] == "system":
                system_msg = m["content"]
            else:
                chat_msgs.append(m)

        body = {
            "model": self.model or "claude-sonnet-4-6",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": chat_msgs,
        }
        if system_msg:
            body["system"] = system_msg

        payload = json.dumps(body).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            },
        )

        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        return data["content"][0]["text"]

    def _detect_model(self):
        """Auto-detect the loaded model from LM Studio."""
        url = f"{self.api_url.rstrip('/')}/models"
        try:
            req = urllib.request.Request(url, headers={
                "Authorization": f"Bearer {self.api_key}"
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            models = data.get("data", [])
            if models:
                return models[0].get("id", "default")
        except Exception:
            pass
        return "default"

    def is_reachable(self):
        """Check if the API endpoint is responding."""
        try:
            url = f"{self.api_url.rstrip('/')}/models"
            req = urllib.request.Request(url, headers={
                "Authorization": f"Bearer {self.api_key}"
            })
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except Exception:
            return False


def get_client(**kwargs):
    """Factory function. Creates an LLMClient with env var defaults."""
    return LLMClient(**kwargs)
