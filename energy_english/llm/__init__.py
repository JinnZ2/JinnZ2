# energy_english/llm/__init__.py
"""
LLM clients for the model route.

Each client is a callable taking a prompt string and returning a
response string — the same shape ``GatedDispatcher`` expects, so any
of them drops in as the dispatcher's ``model_callable``. Stdlib only
(``urllib`` + ``json``); no provider-SDK dependency.

Default system prompt is loaded from ``system_prompt.md`` (the
``§2 Tight version``) so every model call ships with the
energy_english constraint grammar in front of it.

Available clients:

- ``ClaudeClient``  — Anthropic Messages API
- ``OpenAIClient``  — OpenAI Chat Completions API
- ``GeminiClient``  — Google Generative AI API

API keys come from environment variables by default
(``ANTHROPIC_API_KEY``, ``OPENAI_API_KEY``, ``GOOGLE_API_KEY``);
caller can override per instance. Tests inject a custom opener so
``urlopen`` is fully mockable.
"""

from energy_english.llm.base import (
    DEFAULT_SYSTEM_PROMPT,
    LLMClient,
    LLMError,
    load_default_system_prompt,
)
from energy_english.llm.claude import ClaudeClient
from energy_english.llm.gemini import GeminiClient
from energy_english.llm.openai import OpenAIClient


__all__ = [
    "ClaudeClient",
    "DEFAULT_SYSTEM_PROMPT",
    "GeminiClient",
    "LLMClient",
    "LLMError",
    "OpenAIClient",
    "load_default_system_prompt",
]
