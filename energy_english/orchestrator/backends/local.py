# energy_english/orchestrator/backends/local.py
"""
LocalRuntime — runs the sim as a subprocess on this machine.

The "direct" backend in the AWS / Docker / direct / self-hosted set.
No external dependencies beyond a Python interpreter (which is the
runtime's own).

Use when:
- developing a sim
- the sim is fast and runs on the laptop / cab compute
- there is no need for isolation or remote execution


Ontology: every name in this module names a state variable on a
curve, not a permanent identity. See ``DIFFERENTIAL_FRAME.md`` at
the repo root.
"""

from __future__ import annotations

import shlex
import sys
from typing import List, Optional

from energy_english.orchestrator.backends._subprocess_base import SubprocessRuntime
from energy_english.orchestrator.runtime import RunRequest


class LocalRuntime(SubprocessRuntime):
    """
    Runs ``request.entrypoint`` directly. If ``entrypoint`` ends in
    ``.py`` (or ``python_executable`` is set), the configured Python
    interpreter is used; otherwise the entrypoint is invoked as-is
    so shell scripts and compiled binaries also work.
    """

    name = "local"

    def __init__(self, python_executable: Optional[str] = None):
        self.python_executable = python_executable or sys.executable

    def _build_command(
        self,
        request: RunRequest,
        config_path: str,
        output_path: str,
    ) -> List[str]:
        ep = request.entrypoint
        argv = shlex.split(ep) if " " in ep else [ep]
        if ep.endswith(".py") or "python" in ep:
            return [self.python_executable, *argv]
        return argv
