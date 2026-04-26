# energy_english/tests/test_llm.py
"""
Tests for the LLM clients.

Every test injects a fake opener so no real network calls are made.
The tests assert: request URL + method + headers + body shape, and
correct extraction of the text from each provider's response shape.
"""

import json
import unittest
import urllib.error
import urllib.request
from io import BytesIO

from energy_english.llm import (
    ClaudeClient,
    DEFAULT_SYSTEM_PROMPT,
    GeminiClient,
    LLMError,
    OpenAIClient,
    load_default_system_prompt,
)


# ── Fake HTTP plumbing ──────────────────────────────────────────


class _FakeResponse:
    def __init__(self, body: bytes, status: int = 200):
        self._body = body
        self.status = status

    def read(self) -> bytes:
        return self._body


class _FakeOpener:
    """A urlopen substitute. Records every request and returns a queued response."""

    def __init__(self, response: _FakeResponse):
        self.response = response
        self.calls = []

    def open(self, req: urllib.request.Request, timeout=None):
        self.calls.append({
            "url": req.full_url,
            "method": req.get_method(),
            "headers": dict(req.header_items()),
            "body": req.data,
            "timeout": timeout,
        })
        return self.response


def _err_opener(status, body=b"upstream error"):
    """An opener that raises HTTPError on every call."""
    class _ErrOpener:
        def __init__(self):
            self.calls = []

        def open(self, req, timeout=None):
            self.calls.append(req.full_url)
            err = urllib.error.HTTPError(
                req.full_url, status, "boom", {}, BytesIO(body),
            )
            raise err
    return _ErrOpener()


# ── Default system prompt ──────────────────────────────────────


class DefaultSystemPrompt(unittest.TestCase):

    def test_inlined_default_is_loaded_when_no_path_given(self):
        s = load_default_system_prompt()
        self.assertEqual(s, DEFAULT_SYSTEM_PROMPT)
        self.assertIn("ENERGY ENGLISH MODE", s)
        self.assertIn("Project every claim onto a triple", s)


# ── Claude ─────────────────────────────────────────────────────


class ClaudeRequest(unittest.TestCase):

    def _opener(self, text="hello world"):
        body = json.dumps({
            "content": [{"type": "text", "text": text}],
        }).encode("utf-8")
        return _FakeOpener(_FakeResponse(body))

    def test_request_shape_includes_system_messages_and_auth(self):
        op = self._opener()
        client = ClaudeClient(api_key="test-key", opener=op)
        out = client("front_A drives front_B")
        self.assertEqual(out, "hello world")

        call = op.calls[0]
        self.assertEqual(call["method"], "POST")
        self.assertEqual(call["url"], ClaudeClient.endpoint)

        headers = {k.lower(): v for k, v in call["headers"].items()}
        self.assertEqual(headers.get("x-api-key"), "test-key")
        self.assertEqual(headers.get("anthropic-version"),
                         ClaudeClient.api_version)
        self.assertEqual(headers.get("content-type"), "application/json")

        body = json.loads(call["body"])
        self.assertEqual(body["model"], ClaudeClient.default_model())
        # System slot carries the energy_english system prompt
        self.assertIn("ENERGY ENGLISH MODE", body["system"])
        # User message carries the prompt
        self.assertEqual(body["messages"][0]["role"], "user")
        self.assertEqual(body["messages"][0]["content"], "front_A drives front_B")

    def test_extracts_text_from_multi_block_content(self):
        body = json.dumps({
            "content": [
                {"type": "text", "text": "first "},
                {"type": "tool_use", "name": "ignored"},
                {"type": "text", "text": "second"},
            ],
        }).encode("utf-8")
        op = _FakeOpener(_FakeResponse(body))
        client = ClaudeClient(api_key="k", opener=op)
        self.assertEqual(client("x"), "first second")

    def test_no_api_key_raises(self):
        client = ClaudeClient(api_key="", opener=self._opener())
        with self.assertRaises(LLMError):
            client("x")

    def test_http_error_wrapped(self):
        op = _err_opener(status=429)
        client = ClaudeClient(api_key="k", opener=op)
        with self.assertRaises(LLMError) as ctx:
            client("x")
        self.assertIn("429", str(ctx.exception))


# ── OpenAI ─────────────────────────────────────────────────────


class OpenAIRequest(unittest.TestCase):

    def _opener(self, text="ok"):
        body = json.dumps({
            "choices": [
                {"message": {"role": "assistant", "content": text}},
            ],
        }).encode("utf-8")
        return _FakeOpener(_FakeResponse(body))

    def test_request_shape_includes_bearer_and_messages(self):
        op = self._opener("response text")
        client = OpenAIClient(api_key="sk-test", opener=op)
        out = client("front_A drives front_B")
        self.assertEqual(out, "response text")

        call = op.calls[0]
        self.assertEqual(call["method"], "POST")
        self.assertEqual(call["url"], OpenAIClient.endpoint)

        headers = {k.lower(): v for k, v in call["headers"].items()}
        self.assertEqual(headers.get("authorization"), "Bearer sk-test")

        body = json.loads(call["body"])
        self.assertEqual(body["model"], OpenAIClient.default_model())
        self.assertEqual(body["messages"][0]["role"], "system")
        self.assertIn("ENERGY ENGLISH MODE", body["messages"][0]["content"])
        self.assertEqual(body["messages"][1]["role"], "user")
        self.assertEqual(body["messages"][1]["content"],
                         "front_A drives front_B")

    def test_no_api_key_raises(self):
        client = OpenAIClient(api_key="", opener=self._opener())
        with self.assertRaises(LLMError):
            client("x")

    def test_missing_choices_raises(self):
        body = json.dumps({}).encode("utf-8")
        op = _FakeOpener(_FakeResponse(body))
        client = OpenAIClient(api_key="k", opener=op)
        with self.assertRaises(LLMError):
            client("x")


# ── Gemini ─────────────────────────────────────────────────────


class GeminiRequest(unittest.TestCase):

    def _opener(self, text="ok"):
        body = json.dumps({
            "candidates": [
                {"content": {"parts": [{"text": text}]}},
            ],
        }).encode("utf-8")
        return _FakeOpener(_FakeResponse(body))

    def test_request_shape_carries_key_query_and_systemInstruction(self):
        op = self._opener("response text")
        client = GeminiClient(api_key="ai-test", opener=op)
        out = client("front_A drives front_B")
        self.assertEqual(out, "response text")

        call = op.calls[0]
        self.assertIn("key=ai-test", call["url"])
        self.assertIn(GeminiClient.default_model(), call["url"])

        body = json.loads(call["body"])
        self.assertIn("systemInstruction", body)
        self.assertIn(
            "ENERGY ENGLISH MODE",
            body["systemInstruction"]["parts"][0]["text"],
        )
        self.assertEqual(body["contents"][0]["role"], "user")
        self.assertEqual(
            body["contents"][0]["parts"][0]["text"],
            "front_A drives front_B",
        )

    def test_extracts_text_from_first_candidate(self):
        body = json.dumps({
            "candidates": [
                {"content": {"parts": [
                    {"text": "first "},
                    {"text": "second"},
                ]}},
            ],
        }).encode("utf-8")
        op = _FakeOpener(_FakeResponse(body))
        client = GeminiClient(api_key="k", opener=op)
        self.assertEqual(client("x"), "first second")

    def test_no_api_key_raises(self):
        client = GeminiClient(api_key="", opener=self._opener())
        with self.assertRaises(LLMError):
            client("x")


# ── Drop-in to GatedDispatcher ────────────────────────────────


class GatedDispatcherIntegration(unittest.TestCase):
    """The whole point: any client is callable(str) -> str, so it
    drops into GatedDispatcher as the model_callable."""

    def test_claude_client_works_as_dispatcher_callable(self):
        body = json.dumps({
            "content": [{"type": "text",
                         "text": "Triples: (a, drives, b, 0.5).\n"
                                 "Silent: c at default."}],
        }).encode("utf-8")
        op = _FakeOpener(_FakeResponse(body))
        client = ClaudeClient(api_key="k", opener=op)

        from energy_english.dispatcher import GatedDispatcher
        from energy_english.findings import Verdict

        d = GatedDispatcher(client, retry_on_block=False)
        rt = d.roundtrip("front_A drives front_B")
        # The model response was structural enough that the gate passes it.
        self.assertIs(rt.output_report.verdict, Verdict.PASS)
        # The dispatcher actually invoked the client.
        self.assertEqual(len(op.calls), 1)


if __name__ == "__main__":
    unittest.main()
