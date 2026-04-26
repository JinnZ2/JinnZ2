# energy_english/dispatcher.py
"""
Layer 2 — gated dispatcher.

Wraps any model callable (an LLM, a simulation + speech-builder
round-trip, a stub, a dictionary lookup) in the Layer 1 constraint
gate. The dispatcher does three things:

1. Pre-flight gate the user's input (permissive — annotates only).
2. Run the model.
3. Post-flight gate the model's response (strict — may BLOCK).

When the response is BLOCKED and ``retry_on_block`` is set, the
dispatcher hands the model a corrective prompt built from the gate's
teaching scaffold (principle + slots + worked example) and tries
again, up to ``max_retries`` times. The teaching scaffold is the
mechanism by which models learn the grammar over time instead of
pattern-matching past it.

The dispatcher is intentionally model-agnostic: ``model_callable`` is
any ``Callable[[str], str]``. Wire it to whichever transport you have
(API, sim pipeline, manual paste).


Ontology: every name in this module names a state variable on a
curve, not a permanent identity. See ``DIFFERENTIAL_FRAME.md`` at
the repo root.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional

from energy_english.gate import ConstraintGate, GateReport, GateVerdict


@dataclass
class RoundTrip:
    """One user-text → response cycle, gated both directions."""

    user_text: str
    response: str
    input_report: GateReport
    output_report: GateReport
    retries: int = 0
    final_blocked: bool = False

    @property
    def verdict(self) -> GateVerdict:
        return self.output_report.verdict


class GatedDispatcher:
    """
    Gate-wraps a model callable. Holds no model state of its own.
    """

    def __init__(
        self,
        model_callable: Callable[[str], str],
        gate: Optional[ConstraintGate] = None,
        *,
        retry_on_block: bool = True,
        max_retries: int = 1,
    ):
        self.model = model_callable
        self.gate = gate or ConstraintGate()
        self.retry_on_block = retry_on_block
        self.max_retries = max_retries

    def roundtrip(self, user_text: str) -> RoundTrip:
        """
        Single user-text → response cycle, gated both directions.

        On a BLOCK with ``retry_on_block=True`` the dispatcher rebuilds
        the prompt with the gate's teaching scaffold appended and
        retries. Up to ``max_retries`` retries; the final report is the
        one from the last attempt regardless of verdict.
        """
        input_report = self.gate.evaluate_input(user_text)
        response = self.model(user_text)
        output_report = self.gate.evaluate_output(
            response, original_input=user_text
        )

        retries = 0
        while (
            output_report.blocked()
            and self.retry_on_block
            and retries < self.max_retries
        ):
            corrective_prompt = self._build_corrective_prompt(user_text, output_report)
            response = self.model(corrective_prompt)
            output_report = self.gate.evaluate_output(
                response, original_input=user_text
            )
            retries += 1

        return RoundTrip(
            user_text=user_text,
            response=response,
            input_report=input_report,
            output_report=output_report,
            retries=retries,
            final_blocked=output_report.blocked(),
        )

    @staticmethod
    def _build_corrective_prompt(user_text: str, blocked_report: GateReport) -> str:
        """
        Build a retry prompt: original input + a structured note that the
        previous response was blocked, with the teaching scaffold
        appended verbatim.
        """
        scaffold = blocked_report.suggested_response or ""
        return (
            f"{user_text}\n\n"
            f"---\n"
            f"Your previous response was blocked by the constraint gate.\n"
            f"Re-emit using this scaffold:\n\n"
            f"{scaffold}"
        )


# ── Convenience: gate a list of texts ────────────────────────────


def evaluate_outputs(
    pairs: List[tuple],
    gate: Optional[ConstraintGate] = None,
) -> List[GateReport]:
    """
    Batch helper. ``pairs`` is a list of ``(user_text, response)``
    tuples. Returns a list of the corresponding output reports.

    Useful for grading transcripts after the fact rather than gating
    in real time.
    """
    g = gate or ConstraintGate()
    return [g.evaluate_output(resp, original_input=user) for user, resp in pairs]
