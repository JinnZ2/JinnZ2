# energy_english/orchestrator/backends/modal_runtime.py
"""
ModalRuntime — invokes a modal.com function as the sim backend.

v0 status: STUB. Instantiation requires the ``modal`` package; otherwise
raises ``BackendUnavailable``. The implementation calls the function
through ``modal.Function.lookup`` so any function deployed under your
modal account is reachable by name.

Use when:
- the sim is long (modal handles minutes-to-hours easily)
- you want serverless GPU/CPU pools without operating them
- you bundle the sim's deps in a modal image at deploy time

modal function contract:

  @app.function(...)
  def run_sim(payload: dict) -> dict:
      cfg = payload['config']             # request_to_config output
      entrypoint = payload['entrypoint']  # opaque sim identifier
      # ... run your sim ...
      return trajectory_dict              # adapt() shape
"""

from __future__ import annotations

import time
from typing import Optional

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
)


try:
    import modal  # type: ignore
    _MODAL_AVAILABLE = True
except ImportError:  # pragma: no cover - environment-dependent
    modal = None  # type: ignore
    _MODAL_AVAILABLE = False


class ModalRuntime(SimRuntime):

    name = "modal"

    def __init__(
        self,
        app_name: str,
        function_name: str = "run_sim",
        function_handle: Optional[object] = None,
    ):
        if not _MODAL_AVAILABLE and function_handle is None:
            raise BackendUnavailable(
                "modal is not installed",
                hint="pip install modal, then run `modal token new` and "
                     "deploy your function via `modal deploy`",
            )
        self.app_name = app_name
        self.function_name = function_name
        self._fn = function_handle or (
            modal.Function.lookup(app_name, function_name) if _MODAL_AVAILABLE
            else None
        )

    @classmethod
    def is_available(cls) -> bool:
        return _MODAL_AVAILABLE

    def run(self, request: RunRequest) -> RunResult:
        payload = {
            "entrypoint": request.entrypoint,
            "config": request_to_config(request),
            "timeout_seconds": request.timeout_seconds,
        }

        start = time.monotonic()
        try:
            data = self._fn.remote(payload)  # type: ignore[union-attr]
        except Exception as e:
            return RunResult(
                success=False,
                duration_seconds=time.monotonic() - start,
                error=f"modal call failed: {e}",
                backend=self.name,
            )
        duration = time.monotonic() - start

        if not isinstance(data, dict):
            return RunResult(
                success=False,
                duration_seconds=duration,
                error=f"modal returned non-dict: {type(data).__name__}",
                backend=self.name,
            )

        try:
            trajectory = adapt(data)
        except TrajectoryFormatError as e:
            return RunResult(
                success=False,
                duration_seconds=duration,
                error=f"trajectory shape invalid: {e}",
                backend=self.name,
                raw_output=data,
            )

        return RunResult(
            success=True,
            trajectory=trajectory,
            duration_seconds=duration,
            backend=self.name,
            raw_output=data,
        )
