# energy_english/llm/openai.py
"""
OpenAI Chat Completions client.

Stdlib only. API key from ``OPENAI_API_KEY`` by default.


Ontology: every name in this module names a state variable on a
curve, not a permanent identity. See ``DIFFERENTIAL_FRAME.md`` at
the repo root.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Optional

from energy_english.llm.base import LLMClient, LLMError


class OpenAIClient(LLMClient):

    name = "openai"
    env_var = "OPENAI_API_KEY"
    endpoint = "https://api.openai.com/v1/chat/completions"

    @classmethod
    def default_model(cls) -> str:
        return "gpt-4o"

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
                "OpenAIClient: no API key. Set OPENAI_API_KEY or pass "
                "api_key= to the constructor."
            )

        body = json.dumps({
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user",   "content": prompt},
            ],
        }).encode("utf-8")

        req = urllib.request.Request(self.endpoint, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")
        req.add_header("Authorization", f"Bearer {self.api_key}")

        try:
            resp = self._open(req)
            raw = resp.read().decode("utf-8")
            status = getattr(resp, "status", 200)
        except urllib.error.HTTPError as e:
            try:
                detail = e.read().decode("utf-8", errors="replace")
            except Exception:
                detail = str(e)
            raise LLMError(f"OpenAI HTTP {e.code}: {detail}") from e
        except urllib.error.URLError as e:
            raise LLMError(f"OpenAI endpoint unreachable: {e.reason}") from e

        if status >= 300:
            raise LLMError(f"OpenAI HTTP {status}: {raw[:500]}")

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as e:
            raise LLMError(f"OpenAI returned non-JSON: {e}") from e

        choices = payload.get("choices")
        if not isinstance(choices, list) or not choices:
            raise LLMError(f"OpenAI response missing 'choices': {payload!r}")
        message = choices[0].get("message", {})
        text = message.get("content", "")
        return text.strip() if isinstance(text, str) else ""
