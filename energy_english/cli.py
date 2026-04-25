# energy_english/cli.py
"""
Interactive shell for the orchestrator.

Usage:

    python -m energy_english
    python -m energy_english --sim multi_front=/sims/multi_front.py
    python -m energy_english --llm claude
    python -m energy_english --llm openai --model gpt-4o
    python -m energy_english --voice whisper
    python -m energy_english --no-archaeology

The shell reads one utterance per turn (line of text by default;
audio-file path if --voice whisper is set), dispatches it through the
router, and renders the response on the same transport. ``quit`` /
``exit`` / EOF stop the loop; ``help`` lists routes; ``routes`` is
an alias.

The model route activates when --llm <provider> is supplied. Without
that flag a model-route input falls through to ``unrouted`` with a
helpful message. The oral_archaeology and cloud_simulation routes
auto-wire when their backends are available.
"""

from __future__ import annotations

import argparse
import sys
from typing import Dict, List, Optional, TextIO

from energy_english.dispatcher import GatedDispatcher
from energy_english.router import (
    OrchestratorRouter,
    ROUTE_CLOUD_SIMULATION,
    ROUTE_MODEL,
    ROUTE_ORAL_ARCHAEOLOGY,
    ROUTE_UNROUTED,
    routable_intents,
)
from energy_english.voice import (
    StdioVoiceTransport,
    VoiceError,
    VoiceTransport,
    WhisperAPIVoiceTransport,
)


PROMPT = "energy_english> "
HELP_TEXT = """\
Routes:
  oral_archaeology  — say "extract physics from <oral form>"
                      e.g. extract physics from inhale for 4, hold for 7,
                      exhale for 8, pause for 4, repeat
  cloud_simulation  — say "run <sim> with <key>=<value>, ..."
                      e.g. run multi_front with iterations=200, amplitude=0.5
  model             — anything else; goes to the gated dispatcher
                      (must be configured via the API; the shell does
                      not start one by default)

Commands:
  help, routes      — show this text
  status            — show which backends are configured
  quit, exit, ^D    — leave
"""


def _build_llm_client(provider: str, model: Optional[str] = None):
    """Return an LLM client instance by provider name. Lazy import so
    the CLI loads even if the llm subpackage is absent."""
    if not provider:
        return None
    p = provider.lower()
    if p == "claude":
        from energy_english.llm import ClaudeClient
        return ClaudeClient(model=model) if model else ClaudeClient()
    if p in ("openai", "gpt"):
        from energy_english.llm import OpenAIClient
        return OpenAIClient(model=model) if model else OpenAIClient()
    if p == "gemini":
        from energy_english.llm import GeminiClient
        return GeminiClient(model=model) if model else GeminiClient()
    raise SystemExit(
        f"--llm: unknown provider {provider!r}; expected one of: "
        "claude, openai, gemini"
    )


def _build_voice(
    mode: str,
    *,
    input_stream: TextIO,
    output_stream: TextIO,
) -> VoiceTransport:
    """Pick a voice transport. Default is stdio; ``whisper`` selects
    the Whisper API transport (which reads audio file paths from its
    audio_source)."""
    m = (mode or "stdio").lower()
    if m == "stdio":
        return StdioVoiceTransport(
            input_stream=input_stream,
            output_stream=output_stream,
        )
    if m == "whisper":
        return WhisperAPIVoiceTransport(
            audio_source=input_stream,
            output_stream=output_stream,
        )
    raise SystemExit(
        f"--voice: unknown mode {mode!r}; expected one of: stdio, whisper"
    )


def _build_router(
    sim_registry: Optional[Dict[str, str]] = None,
    enable_archaeology: bool = True,
    llm_provider: Optional[str] = None,
    llm_model: Optional[str] = None,
    retry_on_block: bool = True,
) -> OrchestratorRouter:
    oral = None
    if enable_archaeology:
        try:
            from oral_archaeology import OralArchaeologyPipeline
            oral = OralArchaeologyPipeline()
        except Exception:  # pragma: no cover - defensive
            oral = None

    cloud = None
    try:
        from energy_english.orchestrator import CloudOrchestrator
        from energy_english.orchestrator.backends.local import LocalRuntime
        cloud = CloudOrchestrator(LocalRuntime())
    except Exception:  # pragma: no cover - defensive
        cloud = None

    model_dispatcher = None
    if llm_provider:
        client = _build_llm_client(llm_provider, model=llm_model)
        if client is not None:
            model_dispatcher = GatedDispatcher(
                client, retry_on_block=retry_on_block,
            )

    router = OrchestratorRouter(
        oral_archaeology=oral,
        cloud_orchestrator=cloud,
        sim_registry=sim_registry or {},
        model_dispatcher=model_dispatcher,
    )
    # The router auto-constructs an archaeology pipeline when given
    # None and the package is available; honour --no-archaeology by
    # clearing it explicitly.
    if not enable_archaeology:
        router.oral_archaeology = None
    return router


def _status_text(router: OrchestratorRouter) -> str:
    lines = ["Backends:"]
    lines.append(
        f"  oral_archaeology  : {'configured' if router.oral_archaeology else 'not configured'}"
    )
    lines.append(
        f"  cloud_simulation  : {'configured' if router.cloud_orchestrator else 'not configured'}"
    )
    lines.append(
        f"  model             : {'configured' if router.model_dispatcher else 'not configured'}"
    )
    if router.sim_registry:
        lines.append("Registered sims:")
        for name, ep in router.sim_registry.items():
            lines.append(f"  {name} -> {ep}")
    lines.append(f"Routable intents: {', '.join(routable_intents())}")
    return "\n".join(lines)


def _parse_argv(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="energy_english",
        description="Interactive shell for the energy_english orchestrator.",
    )
    parser.add_argument(
        "--sim",
        action="append",
        default=[],
        metavar="NAME=ENTRYPOINT",
        help=(
            "register a sim by friendly name. May be repeated. "
            "Example: --sim multi_front=/sims/multi_front.py"
        ),
    )
    parser.add_argument(
        "--no-archaeology",
        action="store_true",
        help="disable the oral_archaeology backend.",
    )
    parser.add_argument(
        "--llm",
        default=None,
        choices=("claude", "openai", "gpt", "gemini"),
        help=(
            "wire a real LLM into the model route. Reads the API key "
            "from ANTHROPIC_API_KEY / OPENAI_API_KEY / GOOGLE_API_KEY."
        ),
    )
    parser.add_argument(
        "--model",
        default=None,
        metavar="NAME",
        help="override the LLM provider's default model (e.g. gpt-4o, "
             "claude-sonnet-4-6, gemini-1.5-pro).",
    )
    parser.add_argument(
        "--no-retry",
        action="store_true",
        help="disable the gate's auto-retry-with-teaching-scaffold "
             "behaviour on blocked model responses.",
    )
    parser.add_argument(
        "--voice",
        default="stdio",
        choices=("stdio", "whisper"),
        help="select voice transport. 'stdio' uses keyboard / line I/O "
             "(default). 'whisper' reads one audio-file path per line "
             "from stdin and transcribes via the OpenAI Whisper API.",
    )
    return parser.parse_args(argv)


def _parse_sim_specs(specs: List[str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for s in specs:
        if "=" not in s:
            raise SystemExit(
                f"--sim must be NAME=ENTRYPOINT (got {s!r})"
            )
        name, ep = s.split("=", 1)
        name = name.strip()
        ep = ep.strip()
        if not name or not ep:
            raise SystemExit(
                f"--sim NAME and ENTRYPOINT must both be non-empty (got {s!r})"
            )
        out[name] = ep
    return out


def main(
    argv: Optional[List[str]] = None,
    *,
    stdin: Optional[TextIO] = None,
    stdout: Optional[TextIO] = None,
    interactive: Optional[bool] = None,
    transport: Optional[VoiceTransport] = None,
) -> int:
    """
    Run the interactive shell.

    ``stdin`` / ``stdout`` default to the real ones; tests pass
    StringIO. ``interactive`` controls whether the prompt is printed —
    when ``stdin`` is a real TTY it defaults to True; otherwise False.

    ``transport`` lets a caller inject a pre-built ``VoiceTransport``
    (used by tests). When None the transport is constructed from the
    parsed CLI args.
    """
    args = _parse_argv(argv)
    sim_registry = _parse_sim_specs(args.sim)
    router = _build_router(
        sim_registry=sim_registry,
        enable_archaeology=not args.no_archaeology,
        llm_provider=args.llm,
        llm_model=args.model,
        retry_on_block=not args.no_retry,
    )

    in_ = stdin or sys.stdin
    out = stdout or sys.stdout

    if interactive is None:
        interactive = bool(getattr(in_, "isatty", lambda: False)())

    voice = transport or _build_voice(
        args.voice, input_stream=in_, output_stream=out,
    )

    if interactive:
        voice.speak(
            f"energy_english :: type 'help' for routes, 'quit' to exit "
            f"(voice={voice.name})"
        )

    while True:
        if interactive and voice.name == "stdio":
            out.write(PROMPT)
            out.flush()

        try:
            line = voice.listen()
        except VoiceError as e:
            voice.speak(f"[voice error] {e}")
            continue

        if line is None:  # EOF
            if interactive:
                out.write("\n")
            return 0
        line = line.strip()
        if not line:
            continue

        low = line.lower()
        if low in ("quit", "exit", ":q"):
            return 0
        if low in ("help", "?", "routes"):
            voice.speak(HELP_TEXT.rstrip())
            continue
        if low == "status":
            voice.speak(_status_text(router))
            continue

        result = router.dispatch(line)
        voice.speak(f"[route: {result.route}]")
        voice.speak(result.response_text.rstrip())


if __name__ == "__main__":  # pragma: no cover - entry point
    raise SystemExit(main())
