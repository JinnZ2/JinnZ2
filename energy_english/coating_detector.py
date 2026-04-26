# energy_english/coating_detector.py
"""
Layer 4 — coating detector for simulation trajectories.

Coating in language is detected by the gate (``gate.py``) using token
overlap, structural cues, and silent-variable vocabulary. Coating in
trajectories is a different beast: the input is a structured run, not
a string, and the signatures are physical, not linguistic.

This module shares only the *shape* of its output with the gate — the
``Verdict`` / ``Finding`` / ``Report`` types from ``findings.py`` —
so that Layer 5 (the optics translator) can speak about both kinds of
coating with a single vocabulary. It does NOT share detection logic.

Trajectory-coating signatures detected here:

- silent_variable          — declared parameter never varied
- untouched_layer          — observable trace that stayed flat
- unexplored_phase_space   — long run with no mode-transition events
- uncorrelated_coupling    — declared coupling whose endpoints don't
                             actually move together
- convergence_to_expected  — final state matches the speaker's
                             prediction (suspicious only in combination
                             with the above; emitted as WARN)

Inputs are kept stdlib-only — ``Trajectory`` is a plain dataclass and
the math is hand-rolled — so this module loads in environments without
numpy or the simulation package.


Ontology: every name in this module names a state variable on a
curve, not a permanent identity. See ``DIFFERENTIAL_FRAME.md`` at
the repo root.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from energy_english.findings import (
    Finding,
    Report,
    SEVERITY_BLOCK,
    SEVERITY_WARN,
    Verdict,
    verdict_from,
)


# ── Trajectory shape ──────────────────────────────────────────────


@dataclass
class Trajectory:
    """
    Structured snapshot of one simulation run.

    The orchestrator (Layer 3) is responsible for building this object
    from whatever the underlying sim returns. The detector treats it as
    opaque structured data; node-name → trace-name mapping happens
    upstream so this module does not need to know about either.
    """

    # Parameter values used in this run (name → value).
    parameters: Dict[str, Any] = field(default_factory=dict)

    # Subset of ``parameters.keys()`` that were actually swept.
    # Anything in ``parameters`` not here is "left at default" → silent.
    varied_parameters: Set[str] = field(default_factory=set)

    # Observable time-series. Each value is a list of floats indexed
    # by iteration. Trace names are how declared couplings reference them.
    traces: Dict[str, List[float]] = field(default_factory=dict)

    # Constraints the speaker asserted: (source_trace, relation, target_trace).
    declared_couplings: List[Tuple[str, str, str]] = field(default_factory=list)

    # Speaker-provided predicted final values per trace. The detector
    # only uses these to flag convergence-to-expected; predictions are
    # never the success criterion.
    expected_finals: Dict[str, float] = field(default_factory=dict)

    # Mode transitions / threshold crossings / bifurcations recorded
    # during the run. An empty list across a long run is a strong
    # unexplored-phase-space signal.
    events: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def num_iterations(self) -> int:
        return max((len(v) for v in self.traces.values()), default=0)


# ── Stdlib-only math helpers ──────────────────────────────────────


def _stddev(xs: List[float]) -> float:
    n = len(xs)
    if n < 2:
        return 0.0
    mean = sum(xs) / n
    return (sum((x - mean) ** 2 for x in xs) / (n - 1)) ** 0.5


def _pearson(xs: List[float], ys: List[float]) -> float:
    n = min(len(xs), len(ys))
    if n < 2:
        return 0.0
    mx = sum(xs[:n]) / n
    my = sum(ys[:n]) / n
    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    dx2 = sum((xs[i] - mx) ** 2 for i in range(n))
    dy2 = sum((ys[i] - my) ** 2 for i in range(n))
    if dx2 == 0 or dy2 == 0:
        return 0.0
    return num / ((dx2 * dy2) ** 0.5)


# ── Teaching scaffolds for trajectory-coating findings ────────────


_TEACHING: Dict[str, Dict[str, str]] = {
    "silent_variable": {
        "principle": "every declared parameter must be swept, or marked silent.",
        "scaffold": (
            "silent: <parameter name>\n"
            "  declared value: <value at default>\n"
            "  why it matters: <coupling or layer this parameter touches>\n"
            "  next sweep: <range and step to test>"
        ),
        "example": (
            "silent: coupling_range\n"
            "  declared value: 20.0 (default)\n"
            "  why it matters: governs whether competition or saturation appears\n"
            "  next sweep: [10, 40] in steps of 5"
        ),
    },
    "untouched_layer": {
        "principle": "an observable that stays flat across the run is a layer the sim never visited.",
        "scaffold": (
            "untouched: <trace name>\n"
            "  observed range: <min..max>\n"
            "  expected variability under coupled dynamics: <yes/no — why>\n"
            "  perturbation to apply: <input that should move it>"
        ),
        "example": (
            "untouched: max_T\n"
            "  observed range: 300.00..300.00\n"
            "  expected variability: yes — thermal_field is in the declared coupling set\n"
            "  perturbation: drive A_carrier higher or extend run length"
        ),
    },
    "unexplored_phase_space": {
        "principle": (
            "no mode transition across a long run is a hint that the basin "
            "of attraction was the input itself."
        ),
        "scaffold": (
            "unexplored: <iterations completed without any event>\n"
            "  mode transitions: 0\n"
            "  threshold crossings: 0\n"
            "  bifurcations: 0\n"
            "  next probe: <perturbation likely to cross a threshold>"
        ),
        "example": (
            "unexplored: 500 iterations, zero events\n"
            "  next probe: increase coupling_range until competition trips,\n"
            "             OR drop frequency_gap until phase-lock event fires"
        ),
    },
    "uncorrelated_coupling": {
        "principle": (
            "a coupling you declared but cannot measure is fabrication. "
            "either drop the coupling claim or vary inputs until the "
            "endpoints actually move together."
        ),
        "scaffold": (
            "uncorrelated: (<source>, <relation>, <target>)\n"
            "  observed correlation: <r>\n"
            "  required to support claim: |r| >= <threshold>\n"
            "  options:\n"
            "    a) drop the declared coupling\n"
            "    b) sweep an input that should drive the source"
        ),
        "example": (
            "uncorrelated: (lock_A, couples, lock_B)\n"
            "  observed correlation: r=0.04\n"
            "  required: |r| >= 0.1 to keep the claim\n"
            "  options:\n"
            "    a) drop the couples claim — fronts may be independent in this regime\n"
            "    b) sweep coupling_range and recheck"
        ),
    },
    "convergence_to_expected": {
        "principle": (
            "the run converged to your prediction. that is suspicious "
            "only when nothing else moved. confirmation is not evidence."
        ),
        "scaffold": (
            "converged: <trace> ended at <final> (you predicted <expected>)\n"
            "  variance during run: <stddev>\n"
            "  events during run: <count>\n"
            "  reading: <independent confirmation, or coating signal — see other findings>"
        ),
        "example": (
            "converged: lock_A ended at 0.10 (you predicted ≈ 0.10)\n"
            "  variance: 0.001\n"
            "  events: 0\n"
            "  reading: combined with unexplored_phase_space — likely coating"
        ),
    },
}


# ── Detector ──────────────────────────────────────────────────────


class CoatingDetector:
    """
    Detects coating in a Trajectory.

    Tunables:
      stddev_floor             — below this, a trace counts as untouched.
      correlation_floor        — below |r|, a declared coupling counts as
                                 uncorrelated.
      expected_tolerance       — |final - expected| <= tolerance counts
                                 as convergence-to-expected.
      unexplored_min_iters     — a run shorter than this won't fire the
                                 unexplored-phase-space finding.
    """

    def __init__(
        self,
        stddev_floor: float = 1e-6,
        correlation_floor: float = 0.1,
        expected_tolerance: float = 0.05,
        unexplored_min_iters: int = 50,
    ):
        self.stddev_floor = stddev_floor
        self.correlation_floor = correlation_floor
        self.expected_tolerance = expected_tolerance
        self.unexplored_min_iters = unexplored_min_iters

    def detect(self, traj: Trajectory) -> Report:
        findings: List[Finding] = []
        findings.extend(self._silent_variables(traj))
        findings.extend(self._untouched_layers(traj))
        findings.extend(self._unexplored_phase_space(traj))
        findings.extend(self._uncorrelated_couplings(traj))
        findings.extend(self._convergence_to_expected(traj))

        return Report(
            verdict=verdict_from(findings),
            findings=findings,
            suggested_response=self._suggested_response(findings),
        )

    # -- detectors ------------------------------------------------

    def _silent_variables(self, traj: Trajectory) -> List[Finding]:
        out: List[Finding] = []
        for name in traj.parameters:
            if name in traj.varied_parameters:
                continue
            out.append(Finding(
                category="silent_variable",
                severity=SEVERITY_WARN,
                span=name,
                rationale=f"parameter '{name}' was used but never varied",
                reframe=(
                    f"sweep '{name}' across a relevant range, or mark it "
                    "explicitly as silent in the next run"
                ),
            ))
        return out

    def _untouched_layers(self, traj: Trajectory) -> List[Finding]:
        out: List[Finding] = []
        for name, trace in traj.traces.items():
            if _stddev(trace) <= self.stddev_floor:
                lo = min(trace) if trace else 0.0
                hi = max(trace) if trace else 0.0
                out.append(Finding(
                    category="untouched_layer",
                    severity=SEVERITY_WARN,
                    span=name,
                    rationale=(
                        f"trace '{name}' had stddev <= {self.stddev_floor:g} "
                        f"(range {lo:g}..{hi:g})"
                    ),
                    reframe=(
                        f"perturb an input that should move '{name}' or extend "
                        "the run until it does"
                    ),
                ))
        return out

    def _unexplored_phase_space(self, traj: Trajectory) -> List[Finding]:
        if traj.num_iterations < self.unexplored_min_iters:
            return []
        if traj.events:
            return []
        return [Finding(
            category="unexplored_phase_space",
            severity=SEVERITY_BLOCK,
            span=f"<{traj.num_iterations} iterations, 0 events>",
            rationale=(
                "no mode transition, threshold crossing, or bifurcation "
                "across the run"
            ),
            reframe=(
                "drive a parameter beyond a threshold; if no crossing fires, "
                "either the regime is genuinely flat or the sim is coating"
            ),
        )]

    def _uncorrelated_couplings(self, traj: Trajectory) -> List[Finding]:
        out: List[Finding] = []
        for source, relation, target in traj.declared_couplings:
            xs = traj.traces.get(source)
            ys = traj.traces.get(target)
            if not xs or not ys:
                # Missing trace — flag as uncorrelated rather than silent
                # so the speaker has to reconcile node ↔ trace mapping.
                out.append(Finding(
                    category="uncorrelated_coupling",
                    severity=SEVERITY_BLOCK,
                    span=f"({source}, {relation}, {target})",
                    rationale=(
                        f"declared coupling references trace(s) not present: "
                        f"{'source missing' if not xs else ''}"
                        f"{', ' if not xs and not ys else ''}"
                        f"{'target missing' if not ys else ''}"
                    ),
                    reframe=(
                        "either drop the coupling claim or add the missing "
                        "trace to the trajectory"
                    ),
                ))
                continue
            r = _pearson(xs, ys)
            if abs(r) < self.correlation_floor:
                out.append(Finding(
                    category="uncorrelated_coupling",
                    severity=SEVERITY_BLOCK,
                    span=f"({source}, {relation}, {target})",
                    rationale=(
                        f"observed correlation r={r:.3f} below floor "
                        f"{self.correlation_floor:g}"
                    ),
                    reframe=(
                        "drop the coupling claim, OR sweep an input that "
                        "should drive the source until correlation appears"
                    ),
                ))
        return out

    def _convergence_to_expected(self, traj: Trajectory) -> List[Finding]:
        out: List[Finding] = []
        for name, expected in traj.expected_finals.items():
            trace = traj.traces.get(name)
            if not trace:
                continue
            final = trace[-1]
            if abs(final - expected) <= self.expected_tolerance:
                out.append(Finding(
                    category="convergence_to_expected",
                    severity=SEVERITY_WARN,
                    span=name,
                    rationale=(
                        f"trace '{name}' converged to expected "
                        f"({final:.4g} vs predicted {expected:.4g})"
                    ),
                    reframe=(
                        "convergence is not confirmation. read this finding "
                        "alongside silent_variable / untouched_layer / "
                        "unexplored_phase_space results."
                    ),
                ))
        return out

    # -- suggested response ---------------------------------------

    def _suggested_response(self, findings: List[Finding]) -> Optional[str]:
        if not findings:
            return None

        # Order categories blocks-first, dedup while preserving order.
        order: List[str] = []
        seen: Set[str] = set()
        sortable = sorted(
            findings,
            key=lambda f: 0 if f.severity == SEVERITY_BLOCK else 1,
        )
        for f in sortable:
            if f.category not in seen and f.category in _TEACHING:
                order.append(f.category)
                seen.add(f.category)

        lines: List[str] = ["Trajectory-coating findings."]
        lines.append("")
        lines.append(f"Categories: {', '.join(order) if order else '—'}")

        for cat in order:
            block = _TEACHING[cat]
            lines.append("")
            lines.append(f"[{cat}]")
            lines.append(f"  principle: {block['principle']}")
            lines.append("  scaffold:")
            for sline in block["scaffold"].splitlines():
                lines.append(f"    {sline}")
            lines.append("  example:")
            for eline in block["example"].splitlines():
                lines.append(f"    {eline}")

        return "\n".join(lines)
