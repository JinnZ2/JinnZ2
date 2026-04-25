# energy_english/cli.py
"""
Interactive shell for the orchestrator.

Usage:

    python -m energy_english
    python -m energy_english --sim multi_front=/sims/multi_front.py
    python -m energy_english --no-coating

The shell reads one prompt per line, dispatches it through the router,
and prints the response. ``quit`` / ``exit`` / EOF stop the loop;
``help`` lists routes; ``routes`` is an alias.

The shell does not configure a model dispatcher by default, since
that requires an actual LLM client. The oral_archaeology and
cloud_simulation routes are wired up automatically when the
respective backends are available.
"""

from __future__ import annotations

import argparse
import sys
from typing import Dict, List, Optional, TextIO

from energy_english.router import (
    OrchestratorRouter,
    ROUTE_CLOUD_SIMULATION,
    ROUTE_MODEL,
    ROUTE_ORAL_ARCHAEOLOGY,
    ROUTE_UNROUTED,
    routable_intents,
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


def _build_router(
    sim_registry: Optional[Dict[str, str]] = None,
    enable_archaeology: bool = True,
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

    router = OrchestratorRouter(
        oral_archaeology=oral,
        cloud_orchestrator=cloud,
        sim_registry=sim_registry or {},
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
) -> int:
    """
    Run the interactive shell.

    ``stdin`` / ``stdout`` default to the real ones; tests pass
    StringIO. ``interactive`` controls whether the prompt is printed —
    when ``stdin`` is a real TTY it defaults to True; otherwise False.
    """
    args = _parse_argv(argv)
    sim_registry = _parse_sim_specs(args.sim)
    router = _build_router(
        sim_registry=sim_registry,
        enable_archaeology=not args.no_archaeology,
    )

    in_ = stdin or sys.stdin
    out = stdout or sys.stdout

    if interactive is None:
        interactive = bool(getattr(in_, "isatty", lambda: False)())

    if interactive:
        out.write("energy_english :: type 'help' for routes, 'quit' to exit\n")
        out.flush()

    while True:
        if interactive:
            out.write(PROMPT)
            out.flush()
        line = in_.readline()
        if not line:  # EOF
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
            out.write(HELP_TEXT)
            out.flush()
            continue
        if low == "status":
            out.write(_status_text(router) + "\n")
            out.flush()
            continue

        result = router.dispatch(line)
        out.write(f"[route: {result.route}]\n")
        out.write(result.response_text)
        if not result.response_text.endswith("\n"):
            out.write("\n")
        out.flush()


if __name__ == "__main__":  # pragma: no cover - entry point
    raise SystemExit(main())
