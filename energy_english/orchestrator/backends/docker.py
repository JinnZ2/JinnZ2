# energy_english/orchestrator/backends/docker.py
"""
DockerRuntime — runs the sim inside a container via the docker CLI.

Images are expected to honour the same ENERGY_ENGLISH_CONFIG /
ENERGY_ENGLISH_OUTPUT contract as LocalRuntime. The runtime bind-mounts
the host config + output paths into the container at fixed locations
and points the env vars at those locations.

Requirements:
- the ``docker`` binary on PATH (overridable via ``docker_bin``)
- the image is locally pullable or already pulled

Use when:
- the sim has heavyweight dependencies you don't want on the host
- you need reproducibility across machines
- you ship sims as images (e.g. on Docker Hub or a registry)


Ontology: every name in this module names a state variable on a
curve, not a permanent identity. See ``DIFFERENTIAL_FRAME.md`` at
the repo root.
"""

from __future__ import annotations

import shutil
from typing import List, Optional

from energy_english.orchestrator.backends._subprocess_base import SubprocessRuntime
from energy_english.orchestrator.runtime import (
    BackendUnavailable,
    RunRequest,
)


class DockerRuntime(SubprocessRuntime):

    name = "docker"

    CONTAINER_CONFIG_PATH = "/ee/config.json"
    CONTAINER_OUTPUT_PATH = "/ee/output.json"

    def __init__(
        self,
        docker_bin: Optional[str] = None,
        extra_run_args: Optional[List[str]] = None,
    ):
        self.docker_bin = docker_bin or "docker"
        self.extra_run_args = list(extra_run_args or [])

    @classmethod
    def is_available(cls) -> bool:
        return shutil.which("docker") is not None

    def ensure_available(self) -> None:
        if shutil.which(self.docker_bin) is None:
            raise BackendUnavailable(
                f"docker binary {self.docker_bin!r} not found on PATH",
                hint="install Docker Desktop or set docker_bin to the binary path",
            )

    def _build_command(
        self,
        request: RunRequest,
        config_path: str,
        output_path: str,
    ) -> List[str]:
        self.ensure_available()

        cmd: List[str] = [
            self.docker_bin, "run", "--rm",
            "-v", f"{config_path}:{self.CONTAINER_CONFIG_PATH}:ro",
            "-v", f"{output_path}:{self.CONTAINER_OUTPUT_PATH}",
            "-e", f"ENERGY_ENGLISH_CONFIG={self.CONTAINER_CONFIG_PATH}",
            "-e", f"ENERGY_ENGLISH_OUTPUT={self.CONTAINER_OUTPUT_PATH}",
        ]
        # Pass through user env vars (so secrets the sim needs flow in)
        for k, v in (request.env or {}).items():
            cmd.extend(["-e", f"{k}={v}"])

        cmd.extend(self.extra_run_args)
        cmd.append(request.entrypoint)  # the image
        return cmd

    def _build_env(self, request: RunRequest, config_path: str, output_path: str):
        # Container env is set via -e flags; host env stays untouched
        # to avoid leaking host paths into the container.
        import os
        env = dict(os.environ)
        return env
