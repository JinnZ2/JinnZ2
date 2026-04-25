# energy_english/tests/test_voice.py
"""Tests for voice transports."""

import io
import json
import os
import tempfile
import unittest
import urllib.error
import urllib.request

from energy_english.voice import (
    StdioVoiceTransport,
    VoiceError,
    WhisperAPIVoiceTransport,
    transport_from_env,
)


# ── Fake HTTP plumbing (shared with test_llm) ───────────────────


class _FakeResponse:
    def __init__(self, body: bytes, status: int = 200):
        self._body = body
        self.status = status

    def read(self) -> bytes:
        return self._body


class _FakeOpener:
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


# ── Stdio transport ────────────────────────────────────────────


class StdioBasic(unittest.TestCase):

    def test_listen_returns_one_line_at_a_time(self):
        in_ = io.StringIO("first\nsecond\n")
        out = io.StringIO()
        t = StdioVoiceTransport(input_stream=in_, output_stream=out)
        self.assertEqual(t.listen(), "first")
        self.assertEqual(t.listen(), "second")

    def test_listen_returns_none_on_eof(self):
        in_ = io.StringIO("")
        t = StdioVoiceTransport(input_stream=in_, output_stream=io.StringIO())
        self.assertIsNone(t.listen())

    def test_speak_writes_with_trailing_newline(self):
        out = io.StringIO()
        t = StdioVoiceTransport(input_stream=io.StringIO(""),
                                output_stream=out)
        t.speak("hello")
        self.assertEqual(out.getvalue(), "hello\n")

    def test_speak_does_not_double_newline(self):
        out = io.StringIO()
        t = StdioVoiceTransport(input_stream=io.StringIO(""),
                                output_stream=out)
        t.speak("hello\n")
        self.assertEqual(out.getvalue(), "hello\n")

    def test_prompt_is_emitted_before_listen(self):
        in_ = io.StringIO("input\n")
        out = io.StringIO()
        t = StdioVoiceTransport(
            input_stream=in_, output_stream=out, prompt="> ",
        )
        t.listen()
        self.assertEqual(out.getvalue(), "> ")


# ── Whisper API transport ──────────────────────────────────────


class WhisperListen(unittest.TestCase):

    def _make_audio_file(self) -> str:
        f = tempfile.NamedTemporaryFile(
            suffix=".wav", delete=False, mode="wb",
        )
        f.write(b"\x00\x01\x02fake-audio-bytes")
        f.close()
        return f.name

    def test_no_api_key_raises(self):
        path = self._make_audio_file()
        try:
            in_ = io.StringIO(path + "\n")
            t = WhisperAPIVoiceTransport(
                api_key="", audio_source=in_,
                output_stream=io.StringIO(),
                opener=_FakeOpener(_FakeResponse(b"")),
            )
            with self.assertRaises(VoiceError):
                t.listen()
        finally:
            os.unlink(path)

    def test_listen_posts_audio_and_returns_text(self):
        path = self._make_audio_file()
        try:
            body = json.dumps({"text": "the beta front drives the chi front"})
            opener = _FakeOpener(_FakeResponse(body.encode()))
            in_ = io.StringIO(path + "\n")
            t = WhisperAPIVoiceTransport(
                api_key="sk-test",
                audio_source=in_,
                output_stream=io.StringIO(),
                opener=opener,
            )
            text = t.listen()
            self.assertEqual(text, "the beta front drives the chi front")

            call = opener.calls[0]
            self.assertEqual(call["method"], "POST")
            self.assertEqual(call["url"], WhisperAPIVoiceTransport.endpoint)

            headers = {k.lower(): v for k, v in call["headers"].items()}
            self.assertEqual(headers.get("authorization"), "Bearer sk-test")
            self.assertTrue(
                headers.get("content-type", "").startswith("multipart/form-data;")
            )
            # body should contain the model field and the audio bytes
            self.assertIn(b'name="model"', call["body"])
            self.assertIn(b"whisper-1", call["body"])
            self.assertIn(b'name="file"', call["body"])
            self.assertIn(b"fake-audio-bytes", call["body"])
        finally:
            os.unlink(path)

    def test_listen_returns_none_on_eof(self):
        in_ = io.StringIO("")
        t = WhisperAPIVoiceTransport(
            api_key="k",
            audio_source=in_,
            output_stream=io.StringIO(),
            opener=_FakeOpener(_FakeResponse(b"")),
        )
        self.assertIsNone(t.listen())

    def test_http_error_wrapped_as_VoiceError(self):
        path = self._make_audio_file()
        try:
            class _ErrOpener:
                def __init__(self):
                    self.calls = []
                def open(self, req, timeout=None):
                    self.calls.append(req.full_url)
                    raise urllib.error.HTTPError(
                        req.full_url, 401, "auth", {},
                        io.BytesIO(b"unauthorized"),
                    )
            in_ = io.StringIO(path + "\n")
            t = WhisperAPIVoiceTransport(
                api_key="bad-key",
                audio_source=in_,
                output_stream=io.StringIO(),
                opener=_ErrOpener(),
            )
            with self.assertRaises(VoiceError) as ctx:
                t.listen()
            self.assertIn("401", str(ctx.exception))
        finally:
            os.unlink(path)


# ── Auto-detect ────────────────────────────────────────────────


class TransportFromEnv(unittest.TestCase):

    def test_default_is_stdio(self):
        # ensure env vars are clear
        old_voice = os.environ.pop("ENERGY_ENGLISH_VOICE", None)
        try:
            t = transport_from_env(output_stream=io.StringIO())
            self.assertIsInstance(t, StdioVoiceTransport)
        finally:
            if old_voice is not None:
                os.environ["ENERGY_ENGLISH_VOICE"] = old_voice

    def test_whisper_selected_when_env_says_so(self):
        old_voice = os.environ.get("ENERGY_ENGLISH_VOICE")
        old_key = os.environ.get("OPENAI_API_KEY")
        try:
            os.environ["ENERGY_ENGLISH_VOICE"] = "whisper"
            os.environ["OPENAI_API_KEY"] = "sk-test"
            t = transport_from_env(output_stream=io.StringIO())
            self.assertIsInstance(t, WhisperAPIVoiceTransport)
        finally:
            if old_voice is None:
                os.environ.pop("ENERGY_ENGLISH_VOICE", None)
            else:
                os.environ["ENERGY_ENGLISH_VOICE"] = old_voice
            if old_key is None:
                os.environ.pop("OPENAI_API_KEY", None)
            else:
                os.environ["OPENAI_API_KEY"] = old_key

    def test_whisper_falls_back_to_stdio_without_key(self):
        old_voice = os.environ.get("ENERGY_ENGLISH_VOICE")
        old_key = os.environ.pop("OPENAI_API_KEY", None)
        try:
            os.environ["ENERGY_ENGLISH_VOICE"] = "whisper"
            t = transport_from_env(output_stream=io.StringIO())
            self.assertIsInstance(t, StdioVoiceTransport)
        finally:
            if old_voice is None:
                os.environ.pop("ENERGY_ENGLISH_VOICE", None)
            else:
                os.environ["ENERGY_ENGLISH_VOICE"] = old_voice
            if old_key is not None:
                os.environ["OPENAI_API_KEY"] = old_key


if __name__ == "__main__":
    unittest.main()
