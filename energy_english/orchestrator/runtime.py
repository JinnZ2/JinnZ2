# energy_english/orchestrator/runtime.py
"""
Layer 3 — runtime abstraction.

The orchestrator does not care *where* a sim runs (local subprocess,
Docker container, AWS Lambda, modal task, self-hosted HTTP service).
It cares that a sim accepts a config and returns a Trajectory. Each
backend implements ``SimRuntime`` and that's it.

The contract every sim follows, regardless of runtime:

1. The sim reads its config from the file path in
   ``$ENERGY_ENGLISH_CONFIG`` (JSON).
2. The sim writes its result Trajectory to the file path in
   ``$ENERGY_ENGLISH_OUTPUT`` (JSON, in the shape ``trajectory_adapter``
   expects).
3. Exit code 0 means success.

For HTTP-backed runtimes the contract becomes a JSON request/response
pair with the same shape; the runtime adapts.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# ── Public exception ─────────────────────────────────────────────


class BackendUnavailable(RuntimeError):
    """
    Raised when a backend cannot be used in the current environment
    (missing SDK, missing binary, missing credentials). Carries an
    install/repair hint in ``hint``.
    """

    def __init__(self, message: str, hint: str = ""):
        super().__init__(message)
        self.hint = hint

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        base = super().__str__()
        return f"{base}\n  hint: {self.hint}" if self.hint else base


# ── Public dataclasses ───────────────────────────────────────────


@dataclass
class RunRequest:
    """
    What to run and with what inputs.

    ``entrypoint`` interpretation depends on the runtime:

    - LocalRuntime          path to a Python script (or executable)
    - DockerRuntime         image reference (``"image:tag"``)
    - HTTPRuntime           ignored (the URL is on the runtime instance)
    - AWSLambdaRuntime      Lambda function name
    - ModalRuntime          fully-qualified function path

    All other fields are forwarded to the sim verbatim via the JSON
    config file (or POST body for HTTP).
    """

    entrypoint: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    varied_parameters: List[str] = field(default_factory=list)
    expected_finals: Dict[str, float] = field(default_factory=dict)
    declared_couplings: List[Tuple[str, str, str]] = field(default_factory=list)
    timeout_seconds: Optional[float] = None
    working_dir: Optional[str] = None
    env: Dict[str, str] = field(default_factory=dict)


@dataclass
class RunResult:
    """
    What came back. ``trajectory`` is a typed Trajectory when the run
    succeeded and the output file parsed cleanly; otherwise None and
    ``error`` carries a short reason. Raw stdout/stderr are kept for
    debugging.
    """

    success: bool
    trajectory: Optional[Any] = None       # Trajectory from coating_detector
    duration_seconds: Optional[float] = None
    stdout: str = ""
    stderr: str = ""
    error: Optional[str] = None
    backend: str = ""
    raw_output: Optional[Dict[str, Any]] = None  # the JSON before adapting


# ── ABC ──────────────────────────────────────────────────────────


class SimRuntime(ABC):
    """A backend that knows how to run a sim and capture its result."""

    name: str = "unknown"

    @classmethod
    def is_available(cls) -> bool:
        """
        True iff this runtime can be used in the current environment.
        Override in subclasses that depend on optional packages or
        binaries.
        """
        return True

    @abstractmethod
    def run(self, request: RunRequest) -> RunResult:
        """Execute ``request`` and return a RunResult."""


# ── Helper: serialise a RunRequest to the on-disk JSON contract ──


def request_to_config(request: RunRequest) -> Dict[str, Any]:
    """
    Serialise a RunRequest into the JSON contract every sim reads.

    Tuples are flattened to lists for JSON compatibility.
    """
    return {
        "parameters": dict(request.parameters),
        "varied_parameters": list(request.varied_parameters),
        "expected_finals": dict(request.expected_finals),
        "declared_couplings": [list(t) for t in request.declared_couplings],
    }
