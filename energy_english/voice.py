# energy_english/voice.py
"""
Voice transport abstraction.

The shape every transport honours:

    transport.listen() -> Optional[str]   # one transcribed utterance
    transport.speak(text: str) -> None    # render text aloud (or print)

The CLI sits on top of a transport. Today's default
(``StdioVoiceTransport``) reads lines from stdin and writes to stdout
— so "voice" is your keyboard. Real voice transports (Whisper STT for
speech → text, OpenAI TTS for text → speech) plug in by satisfying
the same interface.

The orchestrator architecture (``ENERGY_ENGLISH_ORCHESTRATOR.md``)
calls for voice-first interaction so seconds-to-minutes work windows
at fuel stops and weigh stations stay closed-loop. The transport
layer is what makes that possible without hardcoding the I/O modality
into the dispatcher.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from typing import Optional, TextIO


# ── Errors ───────────────────────────────────────────────────────


class VoiceError(RuntimeError):
    """Raised when a voice transport cannot operate (missing key,
    binary, API failure)."""


# ── Base ────────────────────────────────────────────────────────


class VoiceTransport(ABC):
    """One utterance in, one utterance out."""

    name: str = "unknown"

    @abstractmethod
    def listen(self) -> Optional[str]:
        """
        Return one transcribed utterance, or None on EOF / silence.
        Blocks until an utterance is available.
        """

    @abstractmethod
    def speak(self, text: str) -> None:
        """Render ``text`` as voice (or as printed output)."""


# ── Stdio transport (default) ───────────────────────────────────


class StdioVoiceTransport(VoiceTransport):
    """
    Keyboard-as-voice. Reads one line from ``input_stream`` per
    ``listen()`` call; writes to ``output_stream`` for ``speak()``.
    No external dependencies; works in every environment, including
    CI and unit tests.
    """

    name = "stdio"

    def __init__(
        self,
        *,
        input_stream: Optional[TextIO] = None,
        output_stream: Optional[TextIO] = None,
        prompt: str = "",
    ):
        self.input_stream = input_stream or sys.stdin
        self.output_stream = output_stream or sys.stdout
        self.prompt = prompt

    def listen(self) -> Optional[str]:
        if self.prompt:
            self.output_stream.write(self.prompt)
            self.output_stream.flush()
        line = self.input_stream.readline()
        if not line:
            return None
        return line.rstrip("\n\r")

    def speak(self, text: str) -> None:
        self.output_stream.write(text)
        if not text.endswith("\n"):
            self.output_stream.write("\n")
        self.output_stream.flush()


# ── Whisper API transport (real STT) ────────────────────────────


class WhisperAPIVoiceTransport(VoiceTransport):
    """
    Speech → text via OpenAI's Whisper API.

    Each ``listen()`` reads one audio file path from ``audio_source``
    (default: stdin lines, one path per line) and POSTs the bytes to
    the Whisper transcription endpoint. ``speak()`` is delegated to a
    text-output stream — TTS is a separate transport (stub provided
    below; real cloud TTS lives in a future cycle).

    Requires:
      - ``OPENAI_API_KEY`` (or ``api_key=`` constructor arg)
      - one audio file per utterance (the cab's voice recorder writes
        a wav/mp3, the path arrives via the audio_source stream)

    Tests inject a fake opener so no real network is hit.
    """

    name = "whisper_api"
    endpoint = "https://api.openai.com/v1/audio/transcriptions"
    default_model = "whisper-1"

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        audio_source: Optional[TextIO] = None,
        output_stream: Optional[TextIO] = None,
        opener: Optional[urllib.request.OpenerDirector] = None,
        timeout: float = 60.0,
    ):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.model = model or self.default_model
        self.audio_source = audio_source or sys.stdin
        self.output_stream = output_stream or sys.stdout
        self._opener = opener
        self.timeout = timeout

    def listen(self) -> Optional[str]:
        path_line = self.audio_source.readline()
        if not path_line:
            return None
        path = path_line.strip()
        if not path:
            return ""
        return self._transcribe(path)

    def speak(self, text: str) -> None:
        # Plain text out for v0; TTS transport is a separate component.
        self.output_stream.write(text)
        if not text.endswith("\n"):
            self.output_stream.write("\n")
        self.output_stream.flush()

    # -- internals -----------------------------------------------

    def _transcribe(self, audio_path: str) -> str:
        if not self.api_key:
            raise VoiceError(
                "WhisperAPIVoiceTransport: no API key. Set OPENAI_API_KEY "
                "or pass api_key= to the constructor."
            )
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()

        boundary = "----energy-english-whisper-boundary"
        body = self._build_multipart(boundary, audio_path, audio_bytes)
        req = urllib.request.Request(self.endpoint, data=body, method="POST")
        req.add_header(
            "Content-Type", f"multipart/form-data; boundary={boundary}"
        )
        req.add_header("Authorization", f"Bearer {self.api_key}")
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
            raise VoiceError(f"Whisper HTTP {e.code}: {detail}") from e
        except urllib.error.URLError as e:
            raise VoiceError(f"Whisper endpoint unreachable: {e.reason}") from e

        if status >= 300:
            raise VoiceError(f"Whisper HTTP {status}: {raw[:500]}")

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as e:
            raise VoiceError(f"Whisper returned non-JSON: {e}") from e
        text = payload.get("text", "")
        return text.strip() if isinstance(text, str) else ""

    def _open(self, req):
        if self._opener is not None:
            return self._opener.open(req, timeout=self.timeout)
        return urllib.request.urlopen(req, timeout=self.timeout)

    def _build_multipart(
        self,
        boundary: str,
        filename: str,
        audio_bytes: bytes,
    ) -> bytes:
        crlf = b"\r\n"
        parts = []
        # model field
        parts.append(f"--{boundary}".encode())
        parts.append(b'Content-Disposition: form-data; name="model"')
        parts.append(b"")
        parts.append(self.model.encode())
        # file field
        basename = os.path.basename(filename) or "audio.wav"
        parts.append(f"--{boundary}".encode())
        parts.append(
            f'Content-Disposition: form-data; name="file"; filename="{basename}"'
            .encode()
        )
        parts.append(b"Content-Type: application/octet-stream")
        parts.append(b"")
        parts.append(audio_bytes)
        parts.append(f"--{boundary}--".encode())
        parts.append(b"")
        return crlf.join(parts)


# ── Convenience: auto-detect ─────────────────────────────────────


def transport_from_env(
    *,
    output_stream: Optional[TextIO] = None,
) -> VoiceTransport:
    """
    Pick a transport from env vars:

    - ``ENERGY_ENGLISH_VOICE=whisper`` AND ``OPENAI_API_KEY`` set
      → ``WhisperAPIVoiceTransport``
    - otherwise → ``StdioVoiceTransport``
    """
    mode = os.environ.get("ENERGY_ENGLISH_VOICE", "").lower()
    if mode == "whisper" and os.environ.get("OPENAI_API_KEY"):
        return WhisperAPIVoiceTransport(output_stream=output_stream)
    return StdioVoiceTransport(output_stream=output_stream)
