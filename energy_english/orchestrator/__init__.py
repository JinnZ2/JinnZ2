# energy_english/orchestrator/__init__.py
"""
Layer 3 — cloud orchestrator.

CloudOrchestrator is the runtime-agnostic glue. Give it any
``SimRuntime`` (LocalRuntime, DockerRuntime, HTTPRuntime,
AWSLambdaRuntime, ModalRuntime — or your own subclass) and it
exposes a uniform ``run()`` that returns a typed ``RunResult``
with a Trajectory ready for the L4 coating detector.

The orchestrator does not care WHERE the sim runs. The contract is
the same everywhere: read JSON config, write JSON Trajectory.
"""

from __future__ import annotations

from typing import Any, Optional

from energy_english.orchestrator.runtime import (
    BackendUnavailable,
    RunRequest,
    RunResult,
    SimRuntime,
    request_to_config,
)
from energy_english.orchestrator.trajectory_adapter import (
    TrajectoryFormatError,
    adapt,
    adapt_loose,
)


__all__ = [
    "BackendUnavailable",
    "CloudOrchestrator",
    "RunRequest",
    "RunResult",
    "SimRuntime",
    "TrajectoryFormatError",
    "adapt",
    "adapt_loose",
    "request_to_config",
]


class CloudOrchestrator:
    """
    Wraps a SimRuntime. Adds:

    - default timeout that applies when the request doesn't specify one
    - convenience ``run_kwargs`` form that builds a RunRequest inline
    - optional callback hook so the L4 coating detector can run on
      every result without the caller wiring it up by hand
    """

    def __init__(
        self,
        runtime: SimRuntime,
        default_timeout_seconds: Optional[float] = None,
        on_result: Optional[Any] = None,
    ):
        self.runtime = runtime
        self.default_timeout_seconds = default_timeout_seconds
        self.on_result = on_result

    def run(self, request: RunRequest) -> RunResult:
        if request.timeout_seconds is None and self.default_timeout_seconds is not None:
            # Don't mutate the caller's request; rebuild with default timeout.
            request = RunRequest(
                entrypoint=request.entrypoint,
                parameters=request.parameters,
                varied_parameters=request.varied_parameters,
                expected_finals=request.expected_finals,
                declared_couplings=request.declared_couplings,
                timeout_seconds=self.default_timeout_seconds,
                working_dir=request.working_dir,
                env=request.env,
            )

        result = self.runtime.run(request)

        if self.on_result is not None:
            try:
                self.on_result(result)
            except Exception:  # callback errors must not break the orchestrator
                pass

        return result

    def run_kwargs(self, **kwargs) -> RunResult:
        """
        Build a RunRequest from kwargs and run it. Convenience for
        callers that don't want to construct a RunRequest by hand.
        """
        return self.run(RunRequest(**kwargs))
