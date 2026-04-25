# energy_english/router.py
"""
Layer 2 — orchestrator router.

The router is the actual L2 dispatcher in the orchestrator architecture:
voice in → classify intent → route to the right backend → unified
result back.

Backends in v0:

- ``oral_archaeology``  — routes to ``oral_archaeology.OralArchaeologyPipeline``
                          for "extract physics from <oral form>" requests.
- ``model``             — routes to a ``GatedDispatcher`` for everything
                          else; the dispatcher applies the L1 gate to
                          input and output and (when ``retry_on_block``
                          is on) feeds the gate's teaching scaffold back
                          to the model as a corrective prompt.

``GatedDispatcher`` itself is not the router — it is the gated-call
subroutine the router uses for the model route. Future routes (e.g.
a cloud-sim handler at L3) plug in alongside the existing two.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

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
    route) and is None on routes that don't produce it.
    """

    route: str
    response_text: str
    payload: str = ""                  # the slice of user_text the router fed downstream
    archaeology_report: Any = None     # ArchaeologyReport when route == oral_archaeology
    roundtrip: Optional[RoundTrip] = None  # set when route == model

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
    """
    for pattern, label in _ARCHAEOLOGY_PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if m:
            payload = m.group(1).strip().strip(":-").strip()
            if payload:
                return ROUTE_ORAL_ARCHAEOLOGY, payload, label
    return ROUTE_MODEL, text, None


def routable_intents() -> List[str]:
    """Routes the v0 router knows about. Useful for help text."""
    return [ROUTE_ORAL_ARCHAEOLOGY, ROUTE_MODEL]


# ── Router ────────────────────────────────────────────────────────


class OrchestratorRouter:
    """
    Voice → classify → backend.

    Either backend is optional, so the router can be used in
    model-only or archaeology-only configurations. If neither is
    configured for the route a request would take, the result has
    ``route='unrouted'`` and a clear error message in
    ``response_text``.
    """

    def __init__(
        self,
        model_dispatcher: Optional[GatedDispatcher] = None,
        oral_archaeology: Optional[Any] = None,
        archaeology_format_mode: str = "compact",
    ):
        self.model_dispatcher = model_dispatcher
        if oral_archaeology is None and _ORAL_ARCHAEOLOGY_AVAILABLE:
            self.oral_archaeology = OralArchaeologyPipeline()
        else:
            self.oral_archaeology = oral_archaeology
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

        # Default: model route.
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
