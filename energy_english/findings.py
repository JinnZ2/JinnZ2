# energy_english/findings.py
"""
Shared report-shape types for every layer that emits findings.

Layer 1 (the constraint gate, ``gate.py``) and Layer 4 (the coating
detector, ``coating_detector.py``) operate on different inputs — text
vs. structured trajectory — and run different detection logic, so they
do not share detection code. They DO share:

- severity scoring conventions (info / warn / block)
- the verdict triple (PASS / FLAG / BLOCK)
- the finding shape (category, severity, span, rationale, reframe)
- the report shape (verdict, findings, suggested_response)

That shared vocabulary is what lets the eventual optics translator
(Layer 5) speak about both kinds of findings with one grammar.

If you are writing a new detector, return a ``Report`` whose findings
all use the constants below. Keep your category strings consistent
with the existing teaching blocks where applicable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


# ── Severity ──────────────────────────────────────────────────────


SEVERITY_INFO = "info"      # noted, no warning
SEVERITY_WARN = "warn"      # report-level issue, output may still be useful
SEVERITY_BLOCK = "block"    # structural violation


# ── Verdict ───────────────────────────────────────────────────────


class Verdict(Enum):
    PASS = "pass"      # nothing fired
    FLAG = "flag"      # findings present, output may still be useful
    BLOCK = "block"    # structurally violates the grammar


# ── Finding ───────────────────────────────────────────────────────


@dataclass
class Finding:
    """One localized observation from a detector."""

    category: str
    severity: str
    span: str            # the offending substring or a synthetic marker
    rationale: str
    reframe: Optional[str] = None  # how to rewrite or fix this finding


# ── Report ────────────────────────────────────────────────────────


@dataclass
class Report:
    """Aggregate result from a detector."""

    verdict: Verdict
    findings: List[Finding] = field(default_factory=list)
    suggested_response: Optional[str] = None

    def blocked(self) -> bool:
        return self.verdict is Verdict.BLOCK

    def has_category(self, category: str) -> bool:
        return any(f.category == category for f in self.findings)


def verdict_from(findings: List[Finding]) -> Verdict:
    """Compute a verdict from a list of findings using the shared severity convention."""
    if not findings:
        return Verdict.PASS
    if any(f.severity == SEVERITY_BLOCK for f in findings):
        return Verdict.BLOCK
    return Verdict.FLAG
