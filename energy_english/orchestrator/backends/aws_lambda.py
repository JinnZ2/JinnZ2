# energy_english/orchestrator/backends/aws_lambda.py
"""
AWSLambdaRuntime — invokes an AWS Lambda function as the sim backend.

v0 status: STUB. The class is fully usable iff ``boto3`` is installed
*and* AWS credentials are available; otherwise instantiation raises
``BackendUnavailable`` with an install hint. The implementation is
fully wired but is unverified against a live Lambda function in this
package — write a smoke test against your own function before relying
on it in production.

Use when:
- the sim is short (Lambda's max timeout is 15 minutes)
- you want pay-per-invocation pricing
- the sim fits in a Lambda layer or container image

Lambda function contract (your handler must implement this):

  def handler(event, context):
      cfg = event['config']               # request_to_config output
      entrypoint = event['entrypoint']    # opaque sim identifier
      # ... run your sim ...
      return trajectory_dict              # adapt() shape


Ontology: every name in this module names a state variable on a
curve, not a permanent identity. See ``DIFFERENTIAL_FRAME.md`` at
the repo root.
"""

from __future__ import annotations

import json
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
    import boto3  # type: ignore
    _BOTO3_AVAILABLE = True
except ImportError:  # pragma: no cover - environment-dependent
    boto3 = None  # type: ignore
    _BOTO3_AVAILABLE = False


class AWSLambdaRuntime(SimRuntime):

    name = "aws_lambda"

    def __init__(
        self,
        function_name: Optional[str] = None,
        region_name: Optional[str] = None,
        client: Optional[object] = None,
    ):
        if not _BOTO3_AVAILABLE and client is None:
            raise BackendUnavailable(
                "boto3 is not installed",
                hint="pip install boto3, then configure AWS credentials "
                     "via the standard AWS env vars or ~/.aws/credentials",
            )
        # function_name on the request takes precedence; this default
        # is used only when request.entrypoint is empty.
        self.default_function_name = function_name
        self._client = client or (
            boto3.client("lambda", region_name=region_name) if _BOTO3_AVAILABLE
            else None
        )

    @classmethod
    def is_available(cls) -> bool:
        return _BOTO3_AVAILABLE

    def run(self, request: RunRequest) -> RunResult:
        function_name = request.entrypoint or self.default_function_name
        if not function_name:
            return RunResult(
                success=False,
                error="no Lambda function name supplied",
                backend=self.name,
            )

        payload = json.dumps({
            "entrypoint": function_name,
            "config": request_to_config(request),
            "timeout_seconds": request.timeout_seconds,
        }).encode("utf-8")

        start = time.monotonic()
        try:
            resp = self._client.invoke(  # type: ignore[union-attr]
                FunctionName=function_name,
                InvocationType="RequestResponse",
                Payload=payload,
            )
        except Exception as e:  # boto3 raises a wide family of errors
            return RunResult(
                success=False,
                duration_seconds=time.monotonic() - start,
                error=f"lambda invoke failed: {e}",
                backend=self.name,
            )

        duration = time.monotonic() - start
        status_code = resp.get("StatusCode", 0)
        function_error = resp.get("FunctionError")
        body_raw = resp.get("Payload")
        body = body_raw.read() if hasattr(body_raw, "read") else body_raw or b""

        if status_code >= 300 or function_error:
            return RunResult(
                success=False,
                duration_seconds=duration,
                error=f"lambda status={status_code} fn_error={function_error}",
                stderr=body.decode("utf-8", errors="replace"),
                backend=self.name,
            )

        try:
            data = json.loads(body)
        except (json.JSONDecodeError, TypeError) as e:
            return RunResult(
                success=False,
                duration_seconds=duration,
                error=f"non-JSON Lambda response: {e}",
                stderr=body.decode("utf-8", errors="replace") if body else "",
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
