# energy_english/optics.py
"""
Layer 5 — optics translator.

The optics translator is the speech-back layer. It takes findings from
any combination of upstream layers — gate (L1), coating detector (L4),
oral archaeology (L5 plugin) — and renders a unified, verb-first
energy_english summary the orchestrator can speak back to the human.

Two surfaces:

- ``translate(*reports) -> Optics`` — pure data: which findings landed
  in which reading-bucket (observed / silent / diverged / falsifiers
  / interpretations / open).
- ``speak(optics) -> str`` — verb-first energy_english rendering. No
  narration, no closure, no moral framing. Sections empty when the
  bucket is empty.

The translator is decoupled from the gate's teaching scaffold: the
teaching surface is for re-prompting the model; the optics surface is
for speaking to Kavik. Different audiences, different shapes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional

from energy_english.findings import (
    Finding,
    Report,
    SEVERITY_BLOCK,
    SEVERITY_INFO,
    SEVERITY_WARN,
)


# ── Result shape ─────────────────────────────────────────────────


@dataclass
class Optics:
    """
    Constraint-frame view of multi-layer findings.

    Each list holds rendered, human-readable strings; the original
    Finding objects are not preserved here. If you need the structure
    behind a line, walk the input reports.
    """

    observed: List[str] = field(default_factory=list)
    silent: List[str] = field(default_factory=list)
    diverged: List[str] = field(default_factory=list)
    falsifiers: List[str] = field(default_factory=list)
    interpretations: List[str] = field(default_factory=list)
    invitations: List[str] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not any((
            self.observed, self.silent, self.diverged,
            self.falsifiers, self.interpretations, self.invitations,
        ))


# ── Translator ───────────────────────────────────────────────────


class OpticsTranslator:
    """
    Walks any combination of report-shaped inputs and an optional
    ArchaeologyReport, and groups findings by their reading.
    """

    def translate(self, *reports: Any) -> Optics:
        optics = Optics()
        seen_lines: set = set()  # global dedup across reports

        for report in reports:
            if report is None:
                continue
            if hasattr(report, "constraint_geometry"):
                # ArchaeologyReport
                self._absorb_archaeology(report, optics, seen_lines)
            elif hasattr(report, "findings"):
                # Plain Report (gate / coating / validator)
                self._absorb_findings(report.findings, optics, seen_lines)

        return optics

    def speak(self, optics: Optics) -> str:
        """Render the optics as verb-first energy_english."""
        if optics.is_empty():
            return "OPTICS: nothing fired."

        sections: List[tuple] = [
            ("OBSERVED",        optics.observed),
            ("SILENT",          optics.silent),
            ("DIVERGED",        optics.diverged),
            ("FALSIFIERS",      optics.falsifiers),
            ("INTERPRETATIONS", optics.interpretations),
            ("OPEN",            optics.invitations),
        ]

        lines: List[str] = []
        for header, items in sections:
            if not items:
                continue
            lines.append(header)
            for item in items:
                lines.append(f"  - {item}")
            lines.append("")

        return "\n".join(lines).rstrip() + "\n"

    # -- absorption helpers -------------------------------------

    def _absorb_findings(
        self,
        findings: List[Finding],
        optics: Optics,
        seen: set,
    ) -> None:
        for f in findings:
            self._route_finding(f, optics, seen)

    def _absorb_archaeology(
        self,
        report: Any,
        optics: Optics,
        seen: set,
    ) -> None:
        # Couplings the archaeology pulled go into observed.
        for c in (report.couplings or []):
            line = (
                f"({c.get('source','?')}, {c.get('relationship','?')}, "
                f"{c.get('target','?')})"
            )
            if "strength" in c:
                line += f" strength≈{c['strength']}"
            self._add(optics.observed, line, seen)

        # Implicit variables → silent (the encoding asserts them; the
        # sim either has them or it doesn't, which the trajectory
        # validator surfaces separately as missing_trace).
        for v in (report.implicit_variables or []):
            self._add(optics.silent, f"implicit: {v}", seen)

        # Headline interpretation
        if getattr(report, "physics_interpretation", ""):
            self._add(optics.interpretations, report.physics_interpretation, seen)

        # Walk physics + trajectory validation findings
        if report.physics_validation is not None:
            self._absorb_findings(report.physics_validation.findings, optics, seen)
        if report.trajectory_validation is not None:
            self._absorb_findings(
                report.trajectory_validation.findings, optics, seen
            )

    # -- routing rules ------------------------------------------

    def _route_finding(self, f: Finding, optics: Optics, seen: set) -> None:
        cat = f.category

        # ── L1 gate categories ──
        if cat == "narration":
            self._add(optics.invitations, "anchor in triples; drop story arc.", seen)
            return
        if cat == "intention":
            self._add(
                optics.invitations,
                "echo the literal phrase; do not infer intent.",
                seen,
            )
            return
        if cat == "closure":
            self._add(
                optics.invitations,
                "open the loop; replace 'the answer is' with 'the projection is'.",
                seen,
            )
            return
        if cat == "moralization":
            self._add(
                optics.interpretations,
                f"prescriptive verb ({f.span!r}) → reframe as collaborative trajectory.",
                seen,
            )
            return
        if cat == "surface_certainty":
            self._add(
                optics.interpretations,
                f"echoed certainty ({f.span!r}) → mark probability + scope.",
                seen,
            )
            return
        if cat == "invented_relation":
            self._add(
                optics.interpretations,
                f"non-canonical verb ({f.span!r}) → {f.reframe or 'project to canonical'}",
                seen,
            )
            return
        if cat == "coating":  # text-coating
            self._add(
                optics.falsifiers,
                "name silent variables; show triples; list one falsifier.",
                seen,
            )
            return

        # ── L4 trajectory-coating categories ──
        if cat == "silent_variable":
            self._add(optics.silent, f"{f.span} not varied", seen)
            self._add(optics.falsifiers, f"sweep {f.span}", seen)
            return
        if cat == "untouched_layer":
            self._add(optics.silent, f"{f.span} stayed flat", seen)
            self._add(
                optics.falsifiers,
                f"perturb an input that should move {f.span}",
                seen,
            )
            return
        if cat == "unexplored_phase_space":
            self._add(
                optics.falsifiers,
                "drive a parameter beyond a threshold; force a mode transition.",
                seen,
            )
            self._add(
                optics.invitations,
                "if no crossing fires, regime may be flat OR sim may be coating.",
                seen,
            )
            return
        if cat == "uncorrelated_coupling":
            self._add(optics.diverged, f"{f.span} (no measurable correlation)", seen)
            self._add(
                optics.falsifiers,
                f"sweep an input that should drive the source of {f.span}, "
                "or drop the coupling claim.",
                seen,
            )
            return
        if cat == "convergence_to_expected":
            self._add(
                optics.invitations,
                f"convergence on {f.span} matches your prediction — read alongside "
                "silent / untouched / unexplored findings.",
                seen,
            )
            return

        # ── L5 archaeology validation categories ──
        if cat.startswith("physics."):
            if cat == "physics.no_match":
                self._add(
                    optics.invitations,
                    "no physics-library match; sweep a parameter or extend the library.",
                    seen,
                )
            else:
                # Match or partial match
                if f.severity == SEVERITY_INFO and f.reframe:
                    self._add(optics.interpretations, f.reframe, seen)
                elif f.reframe:
                    self._add(
                        optics.interpretations,
                        f"partial: {f.rationale} — {f.reframe}",
                        seen,
                    )
                else:
                    self._add(optics.interpretations, f.rationale, seen)
            return

        if cat == "trajectory.unavailable":
            self._add(
                optics.invitations,
                "no captured trajectory yet; capture one and re-validate.",
                seen,
            )
            return
        if cat == "trajectory.missing_trace":
            self._add(optics.silent, f"trajectory has no trace for {f.span}", seen)
            self._add(
                optics.falsifiers,
                f"add a trace named {f.span!r} to the sim, or drop the implicit-variable claim.",
                seen,
            )
            return
        if cat == "trajectory.match":
            self._add(optics.observed, f"{f.span} matches trajectory", seen)
            return
        if cat == "trajectory.diverge":
            self._add(optics.diverged, f"{f.span} diverges from trajectory", seen)
            self._add(
                optics.falsifiers,
                "extend the sim with the missing physics OR drop the oral coupling claim.",
                seen,
            )
            return

        # ── Unknown category — record under invitations as a hint ──
        rationale = f.rationale or cat
        self._add(optics.invitations, f"unrouted finding [{cat}]: {rationale}", seen)

    @staticmethod
    def _add(bucket: List[str], line: str, seen: set) -> None:
        key = line.strip().lower()
        if key in seen:
            return
        seen.add(key)
        bucket.append(line)
