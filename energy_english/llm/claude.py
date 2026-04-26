# energy_english/llm/claude.py
"""
Anthropic Messages API client.

Stdlib only (urllib + json). API key from ``ANTHROPIC_API_KEY`` by
default. Tests inject a custom opener so the HTTP layer is fully
mockable; no real network calls are required to exercise the client.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Optional

from energy_english.llm.base import LLMClient, LLMError


class ClaudeClient(LLMClient):

    name = "claude"
    env_var = "ANTHROPIC_API_KEY"
    endpoint = "https://api.anthropic.com/v1/messages"
    api_version = "2023-06-01"

    @classmethod
    def default_model(cls) -> str:
        return "claude-sonnet-4-6"

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        opener=None,
        timeout: float = 60.0,
        max_tokens: int = 1024,
        endpoint: Optional[str] = None,
    ):
        super().__init__(
            api_key=api_key, model=model, system_prompt=system_prompt,
            opener=opener, timeout=timeout,
        )
        self.max_tokens = max_tokens
        if endpoint is not None:
            self.endpoint = endpoint

    def __call__(self, prompt: str) -> str:
        if not self.api_key:
            raise LLMError(
                "ClaudeClient: no API key. Set ANTHROPIC_API_KEY or pass "
                "api_key= to the constructor."
            )

        body = json.dumps({
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": self.system_prompt,
            "messages": [{"role": "user", "content": prompt}],
        }).encode("utf-8")

        req = urllib.request.Request(self.endpoint, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")
        req.add_header("X-API-Key", self.api_key)
        req.add_header("Anthropic-Version", self.api_version)

        try:
            resp = self._open(req)
            raw = resp.read().decode("utf-8")
            status = getattr(resp, "status", 200)
        except urllib.error.HTTPError as e:
            try:
                detail = e.read().decode("utf-8", errors="replace")
            except Exception:
                detail = str(e)
            raise LLMError(f"Anthropic HTTP {e.code}: {detail}") from e
        except urllib.error.URLError as e:
            raise LLMError(f"Anthropic endpoint unreachable: {e.reason}") from e

        if status >= 300:
            raise LLMError(f"Anthropic HTTP {status}: {raw[:500]}")

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as e:
            raise LLMError(f"Anthropic returned non-JSON: {e}") from e

        # Messages API: { content: [{ type: "text", text: "..." }, ...] }
        content = payload.get("content")
        if not isinstance(content, list) or not content:
            raise LLMError(
                f"Anthropic response missing 'content' list: {payload!r}"
            )
        chunks = [
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        ]
        return "".join(chunks).strip()
