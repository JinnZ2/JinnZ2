# energy_english/llm/gemini.py
"""
Google Generative AI (Gemini) client.

Stdlib only. API key from ``GOOGLE_API_KEY`` by default. Sent as a
query-string parameter (``?key=<api_key>``) per Google's REST contract.
The system instruction is sent as the ``systemInstruction`` field in
the body.


Ontology: every name in this module names a state variable on a
curve, not a permanent identity. See ``DIFFERENTIAL_FRAME.md`` at
the repo root.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional

from energy_english.llm.base import LLMClient, LLMError


class GeminiClient(LLMClient):

    name = "gemini"
    env_var = "GOOGLE_API_KEY"
    endpoint_template = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/{model}:generateContent"
    )

    @classmethod
    def default_model(cls) -> str:
        return "gemini-1.5-pro"

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
        self._endpoint_override = endpoint

    def _resolve_endpoint(self) -> str:
        base = self._endpoint_override or self.endpoint_template.format(
            model=self.model
        )
        return f"{base}?key={urllib.parse.quote(self.api_key)}"

    def __call__(self, prompt: str) -> str:
        if not self.api_key:
            raise LLMError(
                "GeminiClient: no API key. Set GOOGLE_API_KEY or pass "
                "api_key= to the constructor."
            )

        body = json.dumps({
            "systemInstruction": {
                "role": "system",
                "parts": [{"text": self.system_prompt}],
            },
            "contents": [
                {"role": "user", "parts": [{"text": prompt}]},
            ],
            "generationConfig": {
                "maxOutputTokens": self.max_tokens,
            },
        }).encode("utf-8")

        url = self._resolve_endpoint()
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")

        try:
            resp = self._open(req)
            raw = resp.read().decode("utf-8")
            status = getattr(resp, "status", 200)
        except urllib.error.HTTPError as e:
            try:
                detail = e.read().decode("utf-8", errors="replace")
            except Exception:
                detail = str(e)
            raise LLMError(f"Gemini HTTP {e.code}: {detail}") from e
        except urllib.error.URLError as e:
            raise LLMError(f"Gemini endpoint unreachable: {e.reason}") from e

        if status >= 300:
            raise LLMError(f"Gemini HTTP {status}: {raw[:500]}")

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as e:
            raise LLMError(f"Gemini returned non-JSON: {e}") from e

        # Gemini response: { candidates: [ { content: { parts: [ {text}, ...] } } ] }
        candidates = payload.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            raise LLMError(f"Gemini response missing 'candidates': {payload!r}")
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        chunks = [p.get("text", "") for p in parts if isinstance(p, dict)]
        return "".join(chunks).strip()
