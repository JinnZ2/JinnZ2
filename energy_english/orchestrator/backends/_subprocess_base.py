# energy_english/orchestrator/backends/_subprocess_base.py
"""
Shared base for backends that drive a subprocess (LocalRuntime,
DockerRuntime). Handles config write, command execution, output read,
timeout enforcement, and trajectory adaptation. Concrete subclasses
only have to build the command and supply the environment that
points at the config + output paths.


Ontology: every name in this module names a state variable on a
curve, not a permanent identity. See ``DIFFERENTIAL_FRAME.md`` at
the repo root.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
from abc import abstractmethod
from typing import Dict, List

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


class SubprocessRuntime(SimRuntime):

    @abstractmethod
    def _build_command(
        self,
        request: RunRequest,
        config_path: str,
        output_path: str,
    ) -> List[str]:
        ...

    def _build_env(
        self,
        request: RunRequest,
        config_path: str,
        output_path: str,
    ) -> Dict[str, str]:
        env = dict(os.environ)
        env.update(request.env or {})
        env["ENERGY_ENGLISH_CONFIG"] = config_path
        env["ENERGY_ENGLISH_OUTPUT"] = output_path
        return env

    def run(self, request: RunRequest) -> RunResult:
        with tempfile.TemporaryDirectory(prefix="ee-orchestrator-") as tmp:
            config_path = os.path.join(tmp, "config.json")
            output_path = os.path.join(tmp, "output.json")

            with open(config_path, "w") as f:
                json.dump(request_to_config(request), f)

            # Pre-create the output file so docker bind-mounts work
            # uniformly. Subclasses may overwrite or rebind.
            with open(output_path, "w") as f:
                f.write("")

            cmd = self._build_command(request, config_path, output_path)
            env = self._build_env(request, config_path, output_path)

            start = time.monotonic()
            try:
                proc = subprocess.run(
                    cmd,
                    cwd=request.working_dir,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=request.timeout_seconds,
                )
            except subprocess.TimeoutExpired as e:
                duration = time.monotonic() - start
                return RunResult(
                    success=False,
                    duration_seconds=duration,
                    stdout=(e.stdout or "") if isinstance(e.stdout, str) else "",
                    stderr=(e.stderr or "") if isinstance(e.stderr, str) else "",
                    error=f"timeout after {request.timeout_seconds}s",
                    backend=self.name,
                )
            except FileNotFoundError as e:
                duration = time.monotonic() - start
                return RunResult(
                    success=False,
                    duration_seconds=duration,
                    error=f"executable not found: {e}",
                    backend=self.name,
                )

            duration = time.monotonic() - start
            stdout = proc.stdout or ""
            stderr = proc.stderr or ""

            if proc.returncode != 0:
                return RunResult(
                    success=False,
                    duration_seconds=duration,
                    stdout=stdout,
                    stderr=stderr,
                    error=f"sim exited with code {proc.returncode}",
                    backend=self.name,
                )

            # Read trajectory from output_path
            try:
                with open(output_path) as f:
                    raw = f.read()
                if not raw.strip():
                    return RunResult(
                        success=False,
                        duration_seconds=duration,
                        stdout=stdout,
                        stderr=stderr,
                        error="sim produced no output (output file empty)",
                        backend=self.name,
                    )
                payload = json.loads(raw)
            except (OSError, json.JSONDecodeError) as e:
                return RunResult(
                    success=False,
                    duration_seconds=duration,
                    stdout=stdout,
                    stderr=stderr,
                    error=f"could not read sim output: {e}",
                    backend=self.name,
                )

            try:
                trajectory = adapt(payload)
            except TrajectoryFormatError as e:
                return RunResult(
                    success=False,
                    duration_seconds=duration,
                    stdout=stdout,
                    stderr=stderr,
                    error=f"trajectory shape invalid: {e}",
                    backend=self.name,
                    raw_output=payload,
                )

            return RunResult(
                success=True,
                trajectory=trajectory,
                duration_seconds=duration,
                stdout=stdout,
                stderr=stderr,
                backend=self.name,
                raw_output=payload,
            )
