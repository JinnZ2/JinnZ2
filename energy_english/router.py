# energy_english/router.py
"""
Layer 2 — orchestrator router.

The router is the actual L2 dispatcher in the orchestrator architecture:
voice in → classify intent → route to the right backend → unified
result back.

Backends in v0:

- ``oral_archaeology``    — routes to ``OralArchaeologyPipeline`` for
                            "extract physics from <oral form>" requests.
- ``cloud_simulation``    — routes to ``CloudOrchestrator`` for
                            "run <sim> with <params>" requests, then
                            runs the L4 coating detector on the
                            resulting Trajectory and renders the
                            optics speech as the response_text.
- ``model``               — routes to a ``GatedDispatcher`` for
                            everything else; the dispatcher applies the
                            L1 gate to input and output and may retry
                            with the gate's teaching scaffold.

``GatedDispatcher`` itself is not the router — it is the gated-call
subroutine the router uses for the model route.


Ontology: every name in this module names a state variable on a
curve, not a permanent identity. See ``DIFFERENTIAL_FRAME.md`` at
the repo root.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from energy_english.dispatcher import GatedDispatcher, RoundTrip


# ── Optional dependency: oral_archaeology -------------------------
#
# Imported lazily so the router can still be used in a model-only
# configuration where the L5 plugin isn't installed.

try:
    from oral_archaeology import (  # type: ignore
        ArchaeologyReport,
        OralArchaeologyPipeline,
        format_report,
    )
    _ORAL_ARCHAEOLOGY_AVAILABLE = True
except Exception:  # pragma: no cover - defensive
    ArchaeologyReport = None  # type: ignore
    OralArchaeologyPipeline = None  # type: ignore
    format_report = None  # type: ignore
    _ORAL_ARCHAEOLOGY_AVAILABLE = False


# ── Routes ────────────────────────────────────────────────────────


ROUTE_ORAL_ARCHAEOLOGY = "oral_archaeology"
ROUTE_CLOUD_SIMULATION = "cloud_simulation"
ROUTE_MODEL = "model"
ROUTE_UNROUTED = "unrouted"


# ── Result ────────────────────────────────────────────────────────


@dataclass
class RouterResult:
    """
    Unified return shape across all backends.

    ``response_text`` is the right thing to read aloud or print.
    Backend-specific structured data is attached on the typed slot
    (``archaeology_report`` for L5, ``roundtrip`` for the model
    route, ``run_result`` + ``coating_report`` for the cloud-sim
    route) and is None on routes that don't produce it.
    """

    route: str
    response_text: str
    payload: str = ""                  # the slice of user_text the router fed downstream
    archaeology_report: Any = None     # ArchaeologyReport when route == oral_archaeology
    roundtrip: Optional[RoundTrip] = None  # set when route == model
    run_result: Any = None             # RunResult when route == cloud_simulation
    coating_report: Any = None         # Report when route == cloud_simulation and trajectory was captured

    @property
    def blocked(self) -> bool:
        if self.roundtrip is not None:
            return self.roundtrip.final_blocked
        return False


# ── Intent classification ─────────────────────────────────────────
#
# Patterns are coarse on purpose. False positives go to the model
# route by design — better to send something to the model than to
# silently misroute.

_SIMULATION_PATTERNS: Tuple[Tuple[str, str], ...] = (
    (
        r"\brun\s+(?:sim\s+|simulation\s+)?(\S+)(?:\s+with\s+(.+))?$",
        "run <sim> [with <params>]",
    ),
    (
        r"\bsimulate\s+(\S+)(?:\s+with\s+(.+))?$",
        "simulate <sim> [with <params>]",
    ),
    (
        r"\bexecute\s+(?:sim\s+)?(\S+)(?:\s+with\s+(.+))?$",
        "execute <sim> [with <params>]",
    ),
)


def _parse_sim_params(text: Optional[str]) -> Dict[str, Any]:
    """
    Parse ``"key=value, key2=value2"`` into a dict with simple type
    inference: ints, then floats, else strings. Empty / None input
    returns an empty dict.
    """
    if not text:
        return {}
    out: Dict[str, Any] = {}
    for part in text.split(","):
        part = part.strip()
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        k = k.strip()
        v = v.strip()
        if not k:
            continue
        try:
            out[k] = int(v)
        except ValueError:
            try:
                out[k] = float(v)
            except ValueError:
                out[k] = v
    return out


_ARCHAEOLOGY_PATTERNS: Tuple[Tuple[str, str], ...] = (
    (
        r"\bextract\s+(?:the\s+)?(?:physics|constraints?|geometry|"
        r"the\s+geometry)\s+from\s*[:\-]?\s*(.+)",
        "extract <X> from",
    ),
    (
        r"\bdecode\s+(?:this\s+|the\s+)?(?:breathing(?:\s+protocol)?|"
        r"dance|story|ritual|protocol|tradition|chant|song)\s*[:\-]?\s*(.+)",
        "decode this <form>",
    ),
    (
        r"\b(?:what|which)\s+(?:physics|geometry|constraints?)\s+"
        r"(?:is|are)\s+(?:encoded\s+)?(?:in)\s*[:\-]?\s*(.+)",
        "what <X> is encoded in",
    ),
    (
        r"\b(?:run\s+)?(?:oral\s+)?archaeology\s+(?:on|for)\s*[:\-]?\s*(.+)",
        "archaeology on",
    ),
    (
        r"\banaly[sz]e\s+(?:this\s+|the\s+)?(?:story|breathing(?:\s+protocol)?|"
        r"dance|ritual|tradition|chant|song)\s*[:\-]?\s*(.+)",
        "analyze this <form>",
    ),
    (
        r"\b(?:physics|geometry|constraint\s+geometry)\s+in\s+(?:this\s+|the\s+)?"
        r"(?:breathing|dance|story|ritual)\s*[:\-]?\s*(.+)",
        "physics in this <form>",
    ),
)


def classify(text: str) -> Tuple[str, str, Optional[str]]:
    """
    Classify a user input.

    Returns ``(route, payload, matched_pattern_label)``. For the model
    route, ``payload`` is the original ``text`` and the label is None.

    Archaeology patterns are checked before simulation patterns because
    "extract physics from <sim>" reads as archaeology, not as a sim
    invocation.
    """
    for pattern, label in _ARCHAEOLOGY_PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if m:
            payload = m.group(1).strip().strip(":-").strip()
            if payload:
                return ROUTE_ORAL_ARCHAEOLOGY, payload, label

    for pattern, label in _SIMULATION_PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            entrypoint = m.group(1).strip().strip(":-").strip()
            params_text = (m.group(2) or "").strip()
            if entrypoint:
                # Re-pack as "<entrypoint>||<params>" so dispatch can
                # split without re-running the regex.
                packed = f"{entrypoint}||{params_text}"
                return ROUTE_CLOUD_SIMULATION, packed, label

    return ROUTE_MODEL, text, None


def routable_intents() -> List[str]:
    """Routes the v0 router knows about. Useful for help text."""
    return [
        ROUTE_ORAL_ARCHAEOLOGY,
        ROUTE_CLOUD_SIMULATION,
        ROUTE_MODEL,
    ]


# ── Router ────────────────────────────────────────────────────────


class OrchestratorRouter:
    """
    Voice → classify → backend.

    Every backend is optional, so the router can be used in any subset
    of model / archaeology / simulation configurations. If the backend
    a request would target is missing, the result has
    ``route='unrouted'`` with a clear error message in
    ``response_text``.

    sim_registry maps friendly sim names to entrypoints (script paths
    for LocalRuntime, image refs for DockerRuntime, function names for
    Lambda, etc.). When the registry is missing or doesn't have a
    matching name, the entrypoint from the voice command is passed
    through to the orchestrator as-is.
    """

    def __init__(
        self,
        model_dispatcher: Optional[GatedDispatcher] = None,
        oral_archaeology: Optional[Any] = None,
        cloud_orchestrator: Optional[Any] = None,
        sim_registry: Optional[Dict[str, str]] = None,
        coating_detector: Optional[Any] = None,
        optics_translator: Optional[Any] = None,
        archaeology_format_mode: str = "compact",
    ):
        self.model_dispatcher = model_dispatcher
        if oral_archaeology is None and _ORAL_ARCHAEOLOGY_AVAILABLE:
            self.oral_archaeology = OralArchaeologyPipeline()
        else:
            self.oral_archaeology = oral_archaeology

        self.cloud_orchestrator = cloud_orchestrator
        self.sim_registry = dict(sim_registry or {})

        # Lazy-construct the L4 detector and L5 optics translator so a
        # fresh router is usable out of the box.
        if coating_detector is None:
            from energy_english.coating_detector import CoatingDetector
            self.coating_detector = CoatingDetector()
        else:
            self.coating_detector = coating_detector
        if optics_translator is None:
            from energy_english.optics import OpticsTranslator
            self.optics_translator = OpticsTranslator()
        else:
            self.optics_translator = optics_translator

        self.archaeology_format_mode = archaeology_format_mode

    def dispatch(
        self,
        user_text: str,
        *,
        trajectory: Any = None,
    ) -> RouterResult:
        """
        Route a single voice/text input to the right backend and return
        a ``RouterResult``. ``trajectory`` is forwarded to the oral
        archaeology pipeline so trajectory-validation runs when both an
        oral form and a captured run are available.
        """
        route, payload, _label = classify(user_text)

        if route == ROUTE_ORAL_ARCHAEOLOGY:
            return self._handle_oral_archaeology(payload, trajectory)

        if route == ROUTE_CLOUD_SIMULATION:
            return self._handle_simulation(payload)

        return self._handle_model(user_text)

    # -- handlers -------------------------------------------------

    def _handle_oral_archaeology(
        self,
        payload: str,
        trajectory: Any,
    ) -> RouterResult:
        if self.oral_archaeology is None:
            return RouterResult(
                route=ROUTE_UNROUTED,
                response_text=(
                    "[router] oral_archaeology pipeline is not configured. "
                    "Install the oral_archaeology package or pass an "
                    "OralArchaeologyPipeline to the router."
                ),
                payload=payload,
            )

        report = self.oral_archaeology.parse(payload, trajectory=trajectory)
        if format_report is not None:
            text = format_report(report, mode=self.archaeology_format_mode)
        else:  # pragma: no cover - defensive; format_report ships with the package
            text = repr(report)

        return RouterResult(
            route=ROUTE_ORAL_ARCHAEOLOGY,
            response_text=text,
            payload=payload,
            archaeology_report=report,
        )

    def _handle_simulation(self, packed_payload: str) -> RouterResult:
        if self.cloud_orchestrator is None:
            return RouterResult(
                route=ROUTE_UNROUTED,
                response_text=(
                    "[router] no cloud_orchestrator configured. "
                    "Pass a CloudOrchestrator to the router to enable "
                    "the cloud_simulation route."
                ),
                payload=packed_payload,
            )

        # Unpack the payload produced by classify(): "<entrypoint>||<params_text>"
        if "||" in packed_payload:
            name_or_path, params_text = packed_payload.split("||", 1)
        else:
            name_or_path, params_text = packed_payload, ""
        name_or_path = name_or_path.strip()
        parameters = _parse_sim_params(params_text)

        entrypoint = self.sim_registry.get(name_or_path, name_or_path)

        # Lazy-import the orchestrator types so the router doesn't
        # require the L3 subpackage just to define the route.
        from energy_english.orchestrator import RunRequest

        request = RunRequest(entrypoint=entrypoint, parameters=parameters)
        run_result = self.cloud_orchestrator.run(request)

        coating_report = None
        if run_result.success and run_result.trajectory is not None:
            coating_report = self.coating_detector.detect(run_result.trajectory)

        # Build the speech surface via the L5 optics translator.
        if run_result.success:
            optics = self.optics_translator.translate(coating_report)
            response_text = self.optics_translator.speak(optics)
        else:
            response_text = (
                f"[cloud_simulation] sim failed on {name_or_path!r}: "
                f"{run_result.error}"
            )

        return RouterResult(
            route=ROUTE_CLOUD_SIMULATION,
            response_text=response_text,
            payload=packed_payload,
            run_result=run_result,
            coating_report=coating_report,
        )

    def _handle_model(self, user_text: str) -> RouterResult:
        if self.model_dispatcher is None:
            return RouterResult(
                route=ROUTE_UNROUTED,
                response_text=(
                    "[router] no model dispatcher configured and the input "
                    "did not match any non-model intent. Configure a "
                    "GatedDispatcher or use a routable phrasing such as "
                    "'extract physics from ...'."
                ),
                payload=user_text,
            )

        rt = self.model_dispatcher.roundtrip(user_text)
        return RouterResult(
            route=ROUTE_MODEL,
            response_text=rt.response,
            payload=user_text,
            roundtrip=rt,
        )
