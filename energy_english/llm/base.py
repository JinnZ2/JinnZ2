# energy_english/llm/base.py
"""
Common base for LLM clients.

The shape every client honours: ``client(prompt: str) -> str``. That
matches ``GatedDispatcher.model_callable`` exactly so any client
drops into the dispatcher without glue.

The default system prompt is the **tight version** from
``energy_english/system_prompt.md`` — short enough to fit in any
provider's system slot, sharp enough to anchor the gate's grammar.


Ontology: every name in this module names a state variable on a
curve, not a permanent identity. See ``DIFFERENTIAL_FRAME.md`` at
the repo root.
"""

from __future__ import annotations

import os
import urllib.request
from abc import ABC, abstractmethod
from typing import Optional


class LLMError(RuntimeError):
    """Raised on any non-2xx response or unparseable body."""


# Tight version of system_prompt.md §2. Inlined so the package can
# load without a path to the markdown file at runtime; identical
# semantics to the on-disk version.
DEFAULT_SYSTEM_PROMPT = """\
ENERGY ENGLISH MODE.

Treat the speaker's words as constraint geometry, not narrative.
Project every claim onto a triple:
  (source, relation, target, strength, scope, polarity, confidence).

Canonical relations: drives, damps, couples, modulates, constrains,
releases, feeds, dissipates, bifurcates, phase_locks, resonates,
synchronizes, decoheres, mediates, shields, amplifies, thresholds,
saturates, hysteretic. Project other verbs onto this set.

Strength, polarity, and confidence are independent. Modal verbs lower
confidence, not strength. Negation flips polarity, does not delete.

DO: surface silent variables, name unexplored phase-space, mark
confidence, hold exploration open, treat "right? / yeah?" as
phase-checks (not rhetoric), echo divergence.

DO NOT: narrate, moralize, assume intention, seek closure, invent
relations, echo "obviously / clearly / of course / naturally" as
given. Reframe those as probability / signal / shared-prior /
dynamics-expected.

COATING is the failure mode: confirming the speaker's hypothesis with
no new constraint surface explored. If you notice it, stop and list
triples, silent variables, and what would falsify the frame.

Style: verb-first, short, lists/tables for structure, no emoji, no
"great question", no closing flourish.
"""


def load_default_system_prompt(path: Optional[str] = None) -> str:
    """
    Read the on-disk ``system_prompt.md`` if ``path`` is given,
    otherwise return the inlined ``DEFAULT_SYSTEM_PROMPT``.

    The on-disk version has both a full and a tight section; this
    helper returns the file as-is so callers can pick which slice
    to use.
    """
    if path is None:
        return DEFAULT_SYSTEM_PROMPT
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class LLMClient(ABC):
    """
    Provider-agnostic interface. Concrete subclasses implement one
    method (``__call__``) that issues a single prompt and returns the
    text response.

    Common construction parameters:

    - ``api_key``  — provider API key. Defaults to the provider's
                     standard env var.
    - ``model``    — provider-specific model name.
    - ``system_prompt`` — system instruction; defaults to
                     ``DEFAULT_SYSTEM_PROMPT``.
    - ``opener``   — optional ``urllib.request.OpenerDirector`` so
                     tests can inject a fake ``urlopen``.
    - ``timeout``  — request timeout in seconds.
    """

    name: str = "unknown"
    env_var: str = ""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        opener: Optional[urllib.request.OpenerDirector] = None,
        timeout: float = 60.0,
    ):
        self.api_key = api_key or os.environ.get(self.env_var, "")
        self.model = model or self.default_model()
        self.system_prompt = (
            system_prompt if system_prompt is not None else DEFAULT_SYSTEM_PROMPT
        )
        self._opener = opener
        self.timeout = timeout

    @classmethod
    def default_model(cls) -> str:
        """Override per provider."""
        return ""

    def _open(self, req: urllib.request.Request):
        if self._opener is not None:
            return self._opener.open(req, timeout=self.timeout)
        return urllib.request.urlopen(req, timeout=self.timeout)

    @abstractmethod
    def __call__(self, prompt: str) -> str:
        """Issue ``prompt`` and return the model's text response."""
