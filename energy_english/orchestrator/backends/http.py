# energy_english/orchestrator/backends/http.py
"""
HTTPRuntime — POST the run request to a user-controlled endpoint.

The "self-hosted" backend in the AWS / Docker / direct / self-hosted
set. The user runs their own service (anywhere — Cloud Run, k8s, EC2,
a Raspberry Pi at home) that accepts POST requests and returns a
trajectory JSON.

The endpoint contract:

POST <url>
Content-Type: application/json
Body:
  {
    "entrypoint":         "<string, sim identifier>",
    "config":             { ... request_to_config(request) ... },
    "timeout_seconds":    <number or null>
  }

Response:
  HTTP 200 with JSON body in trajectory_adapter shape.
  Any non-2xx is treated as failure; the body is returned as ``error``.

Stdlib only — no requests/httpx dependency. ``urllib`` carries the
JSON in and out. ``token`` is added as a Bearer header when supplied.


Ontology: every name in this module names a state variable on a
curve, not a permanent identity. See ``DIFFERENTIAL_FRAME.md`` at
the repo root.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Optional

from energy_english.orchestrator.runtime import (
    RunRequest,
    RunResult,
    SimRuntime,
    request_to_config,
)
from energy_english.orchestrator.trajectory_adapter import (
    TrajectoryFormatError,
    adapt,
)


class HTTPRuntime(SimRuntime):

    name = "http"

    def __init__(
        self,
        endpoint: str,
        token: Optional[str] = None,
        opener: Optional[urllib.request.OpenerDirector] = None,
    ):
        if not endpoint:
            raise ValueError("HTTPRuntime requires a non-empty endpoint URL")
        self.endpoint = endpoint
        self.token = token
        # Tests can inject a custom opener so urlopen is mockable.
        self._opener = opener

    def _open(self, req: urllib.request.Request, timeout: Optional[float]):
        if self._opener is not None:
            return self._opener.open(req, timeout=timeout)
        return urllib.request.urlopen(req, timeout=timeout)

    def run(self, request: RunRequest) -> RunResult:
        body = json.dumps({
            "entrypoint": request.entrypoint,
            "config": request_to_config(request),
            "timeout_seconds": request.timeout_seconds,
        }).encode("utf-8")

        req = urllib.request.Request(self.endpoint, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")
        if self.token:
            req.add_header("Authorization", f"Bearer {self.token}")

        start = time.monotonic()
        try:
            resp = self._open(req, request.timeout_seconds)
            raw = resp.read().decode("utf-8")
            status = getattr(resp, "status", 200)
        except urllib.error.HTTPError as e:
            duration = time.monotonic() - start
            return RunResult(
                success=False,
                duration_seconds=duration,
                error=f"HTTP {e.code}",
                stderr=e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else "",
                backend=self.name,
            )
        except urllib.error.URLError as e:
            duration = time.monotonic() - start
            return RunResult(
                success=False,
                duration_seconds=duration,
                error=f"endpoint unreachable: {e.reason}",
                backend=self.name,
            )

        duration = time.monotonic() - start

        if status >= 300:
            return RunResult(
                success=False,
                duration_seconds=duration,
                error=f"HTTP {status}",
                stderr=raw,
                backend=self.name,
            )

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as e:
            return RunResult(
                success=False,
                duration_seconds=duration,
                error=f"endpoint returned non-JSON: {e}",
                stderr=raw[:1000],
                backend=self.name,
            )

        try:
            trajectory = adapt(payload)
        except TrajectoryFormatError as e:
            return RunResult(
                success=False,
                duration_seconds=duration,
                error=f"trajectory shape invalid: {e}",
                backend=self.name,
                raw_output=payload,
            )

        return RunResult(
            success=True,
            trajectory=trajectory,
            duration_seconds=duration,
            backend=self.name,
            raw_output=payload,
        )
